/**
 * WorkflowEngine — Multi-step task pipeline executor
 *
 * Executes JSON-defined workflow chains (DAGs). Each workflow has:
 * - A trigger (cron, event, or manual)
 * - An ordered list of steps (agent_task, condition, deliver, skill)
 * - Output interpolation between steps via {{stepId.output}}
 */
import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';

const WORKFLOWS_FILE = path.join(process.cwd(), 'workspace', 'workflows.json');

// ─── Types ──────────────────────────────────────────────────────────────────

export interface WorkflowStep {
    id: string;
    action: 'agent_task' | 'condition' | 'deliver' | 'skill';
    /** For agent_task: the prompt (supports {{prev.output}} interpolation) */
    prompt?: string;
    /** For agent_task: optional agent override */
    agentId?: string;
    /** For condition: JS-like expression evaluated against step outputs */
    if?: string;
    /** For condition: next step id on true */
    then?: string;
    /** For condition: next step id on false */
    else?: string;
    /** For deliver: channel type */
    channel?: 'whatsapp' | 'email';
    /** For deliver: target address/number */
    target?: string;
    /** For deliver: message template with {{stepId.output}} */
    template?: string;
    /** For skill: skill name to execute */
    skillName?: string;
    /** For skill: arguments to pass */
    skillArgs?: string;
}

export interface WorkflowTrigger {
    type: 'cron' | 'event' | 'manual';
    cronJobId?: string;
    eventSource?: string;
    eventFilter?: Record<string, string>;
}

export interface Workflow {
    id: string;
    name: string;
    description?: string;
    status: 'enabled' | 'disabled';
    trigger: WorkflowTrigger;
    steps: WorkflowStep[];
    /** LLM provider override for agent_task steps (e.g. 'antigravity', 'openai', 'ollama') */
    model?: string;
    createdAt: string;
    lastRunAt?: string;
    lastRunStatus?: 'success' | 'failed' | 'running';
}

export interface StepResult {
    stepId: string;
    action: string;
    output: string;
    status: 'success' | 'failed' | 'skipped';
    durationMs: number;
}

export interface WorkflowRunResult {
    workflowId: string;
    workflowName: string;
    status: 'success' | 'failed';
    stepResults: StepResult[];
    totalDurationMs: number;
    triggeredAt: string;
}

// ─── Persistence ────────────────────────────────────────────────────────────

function readWorkflows(): Workflow[] {
    try {
        if (!fs.existsSync(WORKFLOWS_FILE)) return [];
        return JSON.parse(fs.readFileSync(WORKFLOWS_FILE, 'utf-8'));
    } catch (e) {
        console.error('[WorkflowEngine] Failed to read workflows.json:', e);
        return [];
    }
}

function writeWorkflows(workflows: Workflow[]) {
    try {
        const dir = path.dirname(WORKFLOWS_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(WORKFLOWS_FILE, JSON.stringify(workflows, null, 2));
    } catch (e) {
        console.error('[WorkflowEngine] Failed to write workflows.json:', e);
    }
}

// ─── Interpolation ──────────────────────────────────────────────────────────

/**
 * Replace {{stepId.output}} placeholders with actual step outputs.
 * Also supports {{prev.output}} for the previous step's output.
 */
function interpolate(template: string, results: Map<string, StepResult>, prevStepId?: string): string {
    return template.replace(/\{\{(\w+)\.output\}\}/g, (match, stepId) => {
        if (stepId === 'prev' && prevStepId) {
            const prev = results.get(prevStepId);
            return prev?.output || '';
        }
        const result = results.get(stepId);
        return result?.output || match;
    });
}

// ─── Condition Evaluator ────────────────────────────────────────────────────

/**
 * Safe condition evaluator. Supports basic string checks:
 * - output.includes('text')
 * - output.length > N
 * - output === 'text'
 * - output.startsWith('text')
 * No eval() — pattern-matched for safety.
 */
function evaluateCondition(expr: string, stepOutputs: Map<string, StepResult>, prevStepId?: string): boolean {
    const prevOutput = prevStepId ? (stepOutputs.get(prevStepId)?.output || '') : '';

    // Replace 'output' with the actual previous step output for evaluation
    const output = prevOutput;

    // Pattern: output.includes('...')
    const includesMatch = expr.match(/output\.includes\(['"](.+?)['"]\)/);
    if (includesMatch) {
        return output.toLowerCase().includes(includesMatch[1]!.toLowerCase());
    }

    // Pattern: output.startsWith('...')
    const startsMatch = expr.match(/output\.startsWith\(['"](.+?)['"]\)/);
    if (startsMatch) {
        return output.toLowerCase().startsWith(startsMatch[1]!.toLowerCase());
    }

    // Pattern: output.length > N
    const lengthMatch = expr.match(/output\.length\s*(>|<|>=|<=|===|==)\s*(\d+)/);
    if (lengthMatch) {
        const op = lengthMatch[1];
        const num = parseInt(lengthMatch[2]!);
        switch (op) {
            case '>': return output.length > num;
            case '<': return output.length < num;
            case '>=': return output.length >= num;
            case '<=': return output.length <= num;
            case '===': case '==': return output.length === num;
        }
    }

    // Pattern: output === '...'
    const equalsMatch = expr.match(/output\s*===?\s*['"](.+?)['"]/);
    if (equalsMatch) {
        return output === equalsMatch[1];
    }

    // Pattern: output !== '...'
    const notEqualsMatch = expr.match(/output\s*!==?\s*['"](.+?)['"]/);
    if (notEqualsMatch) {
        return output !== notEqualsMatch[1];
    }

    console.warn(`[WorkflowEngine] Unrecognized condition expression: ${expr}`);
    return false;
}

// ─── Execution Engine ───────────────────────────────────────────────────────

export class WorkflowEngine {

    /**
     * Execute a workflow by ID with optional trigger context injected into step prompts.
     */
    static async executeWorkflow(workflowId: string, triggerContext?: string): Promise<WorkflowRunResult> {
        const workflows = readWorkflows();
        const workflow = workflows.find(w => w.id === workflowId);

        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        if (workflow.status === 'disabled') {
            throw new Error(`Workflow is disabled: ${workflow.name}`);
        }

        console.log(`\n🔗 [WorkflowEngine] Starting workflow: "${workflow.name}" (${workflow.steps.length} steps)`);

        const startTime = Date.now();
        const stepResults = new Map<string, StepResult>();
        const resultList: StepResult[] = [];
        let currentStepIndex = 0;
        let prevStepId: string | undefined;

        // Mark as running
        workflow.lastRunAt = new Date().toISOString();
        workflow.lastRunStatus = 'running';
        writeWorkflows(workflows);

        try {
            while (currentStepIndex < workflow.steps.length) {
                const step = workflow.steps[currentStepIndex]!;
                const stepStart = Date.now();

                console.log(`  ▶ Step ${currentStepIndex + 1}/${workflow.steps.length}: [${step.action}] ${step.id}`);

                let result: StepResult;

                switch (step.action) {
                    case 'agent_task': {
                        let prompt = step.prompt || '';
                        if (triggerContext && currentStepIndex === 0) {
                            prompt = `[WORKFLOW CONTEXT]\n${triggerContext}\n\n[TASK]\n${prompt}`;
                        }
                        prompt = interpolate(prompt, stepResults, prevStepId);

                        const manager = new ManagerAgent(workflow.model || undefined);
                        try {
                            const output = await manager.processUserRequest(
                                `[SYSTEM WORKFLOW STEP] Execute this step of an automated workflow pipeline. Do not ask for permission. Just do it and summarize results.\n\n${prompt}`
                            );
                            result = { stepId: step.id, action: 'agent_task', output, status: 'success', durationMs: Date.now() - stepStart };
                        } catch (err: any) {
                            result = { stepId: step.id, action: 'agent_task', output: `Error: ${err.message}`, status: 'failed', durationMs: Date.now() - stepStart };
                        }
                        break;
                    }

                    case 'condition': {
                        const expr = step.if || 'true';
                        const condResult = evaluateCondition(expr, stepResults, prevStepId);
                        console.log(`    Condition "${expr}" → ${condResult}`);

                        const nextStepId = condResult ? step.then : step.else;
                        result = { stepId: step.id, action: 'condition', output: `${condResult} → ${nextStepId || 'end'}`, status: 'success', durationMs: Date.now() - stepStart };

                        stepResults.set(step.id, result);
                        resultList.push(result);
                        prevStepId = step.id;

                        // Jump to target step if specified
                        if (nextStepId) {
                            const targetIndex = workflow.steps.findIndex(s => s.id === nextStepId);
                            if (targetIndex >= 0) {
                                currentStepIndex = targetIndex;
                                continue;
                            }
                        }
                        // No target — end workflow
                        break;
                    }

                    case 'deliver': {
                        const message = interpolate(step.template || '{{prev.output}}', stepResults, prevStepId);

                        if (step.channel === 'whatsapp' && step.target) {
                            try {
                                let targetJid = step.target;

                                // Resolve special targets to actual WhatsApp JIDs
                                if (targetJid === 'default' || targetJid === 'admin' || targetJid === 'me') {
                                    // Read the first allowed DM from whatsapp_config.json
                                    const waConfigPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                                    if (fs.existsSync(waConfigPath)) {
                                        const waConfig = JSON.parse(fs.readFileSync(waConfigPath, 'utf-8'));
                                        // Try adminJid first, then first allowedDM
                                        if (waConfig.adminJid) {
                                            targetJid = waConfig.adminJid;
                                        } else if (waConfig.allowedDMs && waConfig.allowedDMs.length > 0) {
                                            const firstDM = waConfig.allowedDMs[0];
                                            const number = typeof firstDM === 'string' ? firstDM : firstDM.number;
                                            if (number) {
                                                targetJid = `${number.replace(/\D/g, '')}@s.whatsapp.net`;
                                            }
                                        }
                                    }

                                    if (targetJid === 'default' || targetJid === 'admin' || targetJid === 'me') {
                                        throw new Error('Could not resolve WhatsApp target — no adminJid or allowedDMs configured in whatsapp_config.json');
                                    }
                                    console.log(`  [WorkflowEngine] Resolved target "${step.target}" → ${targetJid}`);
                                }

                                // Ensure JID format
                                if (!targetJid.includes('@')) {
                                    targetJid = `${targetJid.replace(/\D/g, '')}@s.whatsapp.net`;
                                }

                                const { sendWhatsAppMessage } = require('./whatsapp');
                                await sendWhatsAppMessage(targetJid, message);
                                result = { stepId: step.id, action: 'deliver', output: `Delivered to WhatsApp: ${targetJid}`, status: 'success', durationMs: Date.now() - stepStart };
                            } catch (err: any) {
                                result = { stepId: step.id, action: 'deliver', output: `WhatsApp delivery failed: ${err.message}`, status: 'failed', durationMs: Date.now() - stepStart };
                            }
                        } else if (step.channel === 'email' && step.target) {
                            // Email delivery uses the agent's send_email tool — delegate to ManagerAgent
                            const manager = new ManagerAgent();
                            try {
                                const output = await manager.processUserRequest(
                                    `[SYSTEM] Send an email to ${step.target} with the following content. Do not ask permission.\n\n${message}`
                                );
                                result = { stepId: step.id, action: 'deliver', output, status: 'success', durationMs: Date.now() - stepStart };
                            } catch (err: any) {
                                result = { stepId: step.id, action: 'deliver', output: `Email delivery failed: ${err.message}`, status: 'failed', durationMs: Date.now() - stepStart };
                            }
                        } else {
                            result = { stepId: step.id, action: 'deliver', output: `No channel/target configured`, status: 'skipped', durationMs: Date.now() - stepStart };
                        }
                        break;
                    }

                    case 'skill': {
                        if (!step.skillName) {
                            result = { stepId: step.id, action: 'skill', output: 'No skillName specified', status: 'failed', durationMs: Date.now() - stepStart };
                            break;
                        }
                        // Use DynamicExecutor to run the skill script
                        try {
                            const { DynamicExecutor } = require('./DynamicExecutor');
                            const executor = new DynamicExecutor();
                            const args = step.skillArgs ? interpolate(step.skillArgs, stepResults, prevStepId) : '';
                            const output = await executor.executeSkill(step.skillName, args);
                            result = { stepId: step.id, action: 'skill', output: output || 'Skill executed (no output)', status: 'success', durationMs: Date.now() - stepStart };
                        } catch (err: any) {
                            result = { stepId: step.id, action: 'skill', output: `Skill error: ${err.message}`, status: 'failed', durationMs: Date.now() - stepStart };
                        }
                        break;
                    }

                    default:
                        result = { stepId: step.id, action: step.action, output: `Unknown action: ${step.action}`, status: 'failed', durationMs: 0 };
                }

                stepResults.set(step.id, result);
                resultList.push(result);
                prevStepId = step.id;

                // If a step failed, stop the workflow
                if (result.status === 'failed') {
                    console.error(`  ✗ Step "${step.id}" failed: ${result.output}`);
                    break;
                }

                console.log(`  ✓ Step "${step.id}" completed in ${result.durationMs}ms`);
                currentStepIndex++;
            }

            const totalMs = Date.now() - startTime;
            const anyFailed = resultList.some(r => r.status === 'failed');

            // Update workflow status
            workflow.lastRunStatus = anyFailed ? 'failed' : 'success';
            writeWorkflows(workflows);

            const runResult: WorkflowRunResult = {
                workflowId: workflow.id,
                workflowName: workflow.name,
                status: anyFailed ? 'failed' : 'success',
                stepResults: resultList,
                totalDurationMs: totalMs,
                triggeredAt: workflow.lastRunAt!
            };

            console.log(`🔗 [WorkflowEngine] Workflow "${workflow.name}" ${runResult.status} in ${totalMs}ms (${resultList.length} steps)`);
            return runResult;

        } catch (err: any) {
            workflow.lastRunStatus = 'failed';
            writeWorkflows(workflows);
            throw err;
        }
    }

    // ─── CRUD ───────────────────────────────────────────────────────────────

    static getWorkflows(): Workflow[] {
        return readWorkflows();
    }

    static getWorkflow(id: string): Workflow | undefined {
        return readWorkflows().find(w => w.id === id);
    }

    static saveWorkflow(workflow: Workflow): Workflow {
        const workflows = readWorkflows();
        const existing = workflows.findIndex(w => w.id === workflow.id);
        if (existing >= 0) {
            workflows[existing] = workflow;
        } else {
            workflow.createdAt = workflow.createdAt || new Date().toISOString();
            workflows.push(workflow);
        }
        writeWorkflows(workflows);
        return workflow;
    }

    static deleteWorkflow(id: string): boolean {
        const workflows = readWorkflows();
        const filtered = workflows.filter(w => w.id !== id);
        if (filtered.length === workflows.length) return false;
        writeWorkflows(filtered);
        return true;
    }

    /**
     * Find workflows triggered by a specific cron job ID.
     */
    static getWorkflowsForCron(cronJobId: string): Workflow[] {
        return readWorkflows().filter(
            w => w.status === 'enabled' && w.trigger.type === 'cron' && w.trigger.cronJobId === cronJobId
        );
    }

    /**
     * Find workflows triggered by an event source.
     */
    static getWorkflowsForEvent(source: string): Workflow[] {
        return readWorkflows().filter(
            w => w.status === 'enabled' && w.trigger.type === 'event' && w.trigger.eventSource === source
        );
    }
}

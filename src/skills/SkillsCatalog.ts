import fs from 'node:fs';
import path from 'node:path';

// ═══════════════════════════════════════════════════════════════
// SkillsCatalog — Manages the skills/ directory as a typed catalog.
// Classifies files into "curated" (has .json metadata + assigned to
// an agent) vs "temp" (agent-generated ad-hoc scripts).
// Provides search, archive, and promotion capabilities.
// ═══════════════════════════════════════════════════════════════

export interface CuratedSkill {
    name: string;
    description: string;
    instructions: string;
    language: string;
    ownerAgent: string | null;
    fileSize: number;
    hasScript: boolean;
    scriptExtension: string | null;
}

export interface TempScript {
    filename: string;
    extension: string;
    sizeBytes: number;
    createdAt: string;
    lastModified: string;
    ageDays: number;
}

export interface CatalogStats {
    curatedCount: number;
    tempCount: number;
    tempTotalSizeKB: number;
    archivedCount: number;
}

export interface CatalogRegistry {
    curated: CuratedSkill[];
    temp: TempScript[];
    stats: CatalogStats;
}

const SCRIPT_EXTENSIONS = new Set(['.py', '.sh', '.js', '.ts', '.mjs', '.cjs']);
const DATA_EXTENSIONS = new Set(['.json', '.html', '.txt', '.md', '.csv']);
const IGNORED_FILES = new Set(['package.json', 'package-lock.json', 'node_modules']);

export class SkillsCatalog {
    private skillsDir: string;
    private archiveDir: string;
    private agentsJsonPath: string;

    constructor(rootDir?: string) {
        const root = rootDir || process.cwd();
        this.skillsDir = path.join(root, 'skills');
        this.archiveDir = path.join(this.skillsDir, '_archive');
        this.agentsJsonPath = path.join(root, 'agents.json');
    }

    /**
     * Get the set of curated skill names from agents.json.
     * These are skills explicitly assigned to agents.
     */
    private getCuratedSkillNames(): Set<string> {
        const names = new Set<string>();
        try {
            if (fs.existsSync(this.agentsJsonPath)) {
                const agents = JSON.parse(fs.readFileSync(this.agentsJsonPath, 'utf-8'));
                for (const agent of agents) {
                    if (agent.skills && Array.isArray(agent.skills)) {
                        for (const skill of agent.skills) {
                            names.add(skill);
                        }
                    }
                }
            }
        } catch (e) {
            console.error('[SkillsCatalog] Failed to read agents.json:', e);
        }
        return names;
    }

    /**
     * Get which agent owns a given skill name.
     */
    private getSkillOwner(skillName: string): string | null {
        try {
            if (fs.existsSync(this.agentsJsonPath)) {
                const agents = JSON.parse(fs.readFileSync(this.agentsJsonPath, 'utf-8'));
                for (const agent of agents) {
                    if (agent.skills && Array.isArray(agent.skills) && agent.skills.includes(skillName)) {
                        return agent.name || agent.role || 'Unknown';
                    }
                }
            }
        } catch (e) { }
        return null;
    }

    /**
     * Scan the skills directory and classify all files.
     */
    scan(): CatalogRegistry {
        if (!fs.existsSync(this.skillsDir)) {
            return { curated: [], temp: [], stats: { curatedCount: 0, tempCount: 0, tempTotalSizeKB: 0, archivedCount: 0 } };
        }

        const curatedNames = this.getCuratedSkillNames();
        const curated: CuratedSkill[] = [];
        const temp: TempScript[] = [];
        const now = Date.now();

        // Collect all files (skip _archive, node_modules)
        const allFiles = fs.readdirSync(this.skillsDir).filter(f => {
            if (IGNORED_FILES.has(f)) return false;
            if (f.startsWith('_')) return false; // skip _archive and similar
            return true;
        });

        // Build a map of JSON metadata files
        const jsonFiles = new Set<string>();
        const scriptFiles = new Map<string, string>(); // basename (no ext) → full filename

        for (const file of allFiles) {
            const ext = path.extname(file).toLowerCase();
            const basename = path.basename(file, ext);

            if (ext === '.json') {
                jsonFiles.add(basename);
            } else if (SCRIPT_EXTENSIONS.has(ext)) {
                scriptFiles.set(basename, file);
            }
        }

        // Classify curated skills: have a .json metadata file
        for (const jsonBasename of jsonFiles) {
            const jsonPath = path.join(this.skillsDir, `${jsonBasename}.json`);
            try {
                const metadata = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

                // Only treat as a curated skill if it has a name/description structure
                if (!metadata.name && !metadata.description) continue;

                const scriptFilename = scriptFiles.get(jsonBasename);
                let fileSize = 0;
                let hasScript = false;
                let scriptExtension: string | null = null;

                if (scriptFilename) {
                    const scriptPath = path.join(this.skillsDir, scriptFilename);
                    try {
                        fileSize = fs.statSync(scriptPath).size;
                        hasScript = true;
                        scriptExtension = path.extname(scriptFilename);
                    } catch { }
                    // Remove from scriptFiles so it's not counted as temp
                    scriptFiles.delete(jsonBasename);
                }

                curated.push({
                    name: metadata.name || jsonBasename,
                    description: metadata.description || '',
                    instructions: metadata.instructions || '',
                    language: metadata.language || scriptExtension?.replace('.', '') || 'unknown',
                    ownerAgent: this.getSkillOwner(jsonBasename) || this.getSkillOwner(metadata.name) || null,
                    fileSize,
                    hasScript,
                    scriptExtension,
                });
            } catch (e) {
                // Not a valid skill metadata JSON — skip (it's a data file like quotes_data.json)
            }
        }

        // Remaining scripts are temp files
        let tempTotalSize = 0;
        for (const [basename, filename] of scriptFiles) {
            const filePath = path.join(this.skillsDir, filename);
            try {
                const stat = fs.statSync(filePath);
                const ageDays = Math.floor((now - stat.mtimeMs) / (1000 * 60 * 60 * 24));

                temp.push({
                    filename,
                    extension: path.extname(filename),
                    sizeBytes: stat.size,
                    createdAt: stat.birthtime.toISOString(),
                    lastModified: stat.mtime.toISOString(),
                    ageDays,
                });
                tempTotalSize += stat.size;
            } catch (e) { }
        }

        // Also add non-JSON data files (html, txt, csv) as temp
        for (const file of allFiles) {
            const ext = path.extname(file).toLowerCase();
            const basename = path.basename(file, ext);
            if (DATA_EXTENSIONS.has(ext) && ext !== '.json' && !jsonFiles.has(basename)) {
                const filePath = path.join(this.skillsDir, file);
                try {
                    const stat = fs.statSync(filePath);
                    const ageDays = Math.floor((now - stat.mtimeMs) / (1000 * 60 * 60 * 24));
                    temp.push({
                        filename: file,
                        extension: ext,
                        sizeBytes: stat.size,
                        createdAt: stat.birthtime.toISOString(),
                        lastModified: stat.mtime.toISOString(),
                        ageDays,
                    });
                    tempTotalSize += stat.size;
                } catch { }
            }
        }

        // Sort temp by age (oldest first) for easier archive decisions
        temp.sort((a, b) => b.ageDays - a.ageDays);

        // Count archived files
        let archivedCount = 0;
        try {
            if (fs.existsSync(this.archiveDir)) {
                archivedCount = fs.readdirSync(this.archiveDir).length;
            }
        } catch { }

        return {
            curated,
            temp,
            stats: {
                curatedCount: curated.length,
                tempCount: temp.length,
                tempTotalSizeKB: Math.round(tempTotalSize / 1024),
                archivedCount,
            },
        };
    }

    /**
     * Archive temp scripts older than the specified number of days.
     * Moves files to skills/_archive/ instead of deleting.
     * Returns the number of files archived.
     */
    archiveStale(daysOld: number = 7): { archived: number; freedKB: number; files: string[] } {
        if (!fs.existsSync(this.archiveDir)) {
            fs.mkdirSync(this.archiveDir, { recursive: true });
        }

        const registry = this.scan();
        const stale = registry.temp.filter(t => t.ageDays >= daysOld);
        const archivedFiles: string[] = [];
        let freedBytes = 0;

        for (const script of stale) {
            const src = path.join(this.skillsDir, script.filename);
            const dest = path.join(this.archiveDir, script.filename);
            try {
                // Don't overwrite if already in archive
                if (fs.existsSync(dest)) {
                    // Add timestamp suffix to avoid collision
                    const ext = path.extname(script.filename);
                    const base = path.basename(script.filename, ext);
                    const timestamped = `${base}_${Date.now()}${ext}`;
                    fs.renameSync(src, path.join(this.archiveDir, timestamped));
                } else {
                    fs.renameSync(src, dest);
                }
                archivedFiles.push(script.filename);
                freedBytes += script.sizeBytes;
            } catch (e) {
                console.error(`[SkillsCatalog] Failed to archive ${script.filename}:`, e);
            }
        }

        if (archivedFiles.length > 0) {
            console.log(`[SkillsCatalog] Archived ${archivedFiles.length} stale scripts (${Math.round(freedBytes / 1024)}KB freed).`);
        }

        return {
            archived: archivedFiles.length,
            freedKB: Math.round(freedBytes / 1024),
            files: archivedFiles,
        };
    }

    /**
     * Search skills by name or description (case-insensitive fuzzy match).
     */
    search(query: string): CuratedSkill[] {
        const registry = this.scan();
        const lower = query.toLowerCase();
        return registry.curated.filter(skill =>
            skill.name.toLowerCase().includes(lower) ||
            skill.description.toLowerCase().includes(lower)
        );
    }

    /**
     * Promote a temp script to curated by creating a .json metadata file.
     */
    promote(filename: string, metadata: { name: string; description: string; instructions?: string }): boolean {
        const ext = path.extname(filename);
        const basename = path.basename(filename, ext);
        const jsonPath = path.join(this.skillsDir, `${basename}.json`);
        const scriptPath = path.join(this.skillsDir, filename);

        // Verify the script exists
        if (!fs.existsSync(scriptPath)) {
            throw new Error(`Script not found: ${filename}`);
        }

        // Don't overwrite existing metadata
        if (fs.existsSync(jsonPath)) {
            throw new Error(`Metadata already exists for: ${basename}`);
        }

        const meta = {
            name: metadata.name || basename,
            description: metadata.description || '',
            instructions: metadata.instructions || `Run with: execute_script { "filename": "${filename}" }`,
            language: ext.replace('.', '') || 'python',
        };

        fs.writeFileSync(jsonPath, JSON.stringify(meta, null, 4));
        console.log(`[SkillsCatalog] Promoted ${filename} to curated skill: ${meta.name}`);
        return true;
    }
}

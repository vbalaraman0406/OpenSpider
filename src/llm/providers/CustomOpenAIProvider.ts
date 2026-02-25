import { OpenAIProvider } from './OpenAIProvider';

export class CustomOpenAIProvider extends OpenAIProvider {
    constructor() {
        super(
            process.env.CUSTOM_API_KEY || '',
            process.env.CUSTOM_MODEL || 'local-model',
            process.env.CUSTOM_API_URL || 'http://localhost:1234/v1'
        );
    }
}

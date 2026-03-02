import { defineConfig } from 'vitepress'

export default defineConfig({
    title: 'OpenSpider',
    description: 'Autonomous Multi-Agent System for WhatsApp',
    ignoreDeadLinks: true,
    markdown: {
        languageAlias: {
            'env': 'ini'
        }
    },
    head: [
        ['link', { rel: 'icon', type: 'image/svg+xml', href: '/spider.svg' }],
        ['meta', { name: 'theme-color', content: '#7c3aed' }],
        ['meta', { property: 'og:title', content: 'OpenSpider Docs' }],
        ['meta', { property: 'og:description', content: 'Autonomous Multi-Agent System for WhatsApp — Documentation' }],
    ],
    themeConfig: {
        logo: '/spider.svg',
        siteTitle: 'OpenSpider 🕷️',
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Getting Started', link: '/getting-started' },
            {
                text: 'Guides', items: [
                    { text: 'Configuration', link: '/configuration' },
                    { text: 'Channels', link: '/channels' },
                    { text: 'Dashboard', link: '/dashboard' },
                    { text: 'Tools & Skills', link: '/tools-and-skills' },
                ]
            },
            {
                text: 'Reference', items: [
                    { text: 'CLI Reference', link: '/cli-reference' },
                    { text: 'Architecture', link: '/architecture' },
                    { text: 'Security', link: '/security' },
                    { text: 'Troubleshooting', link: '/troubleshooting' },
                ]
            },
            { text: 'GitHub', link: 'https://github.com/vbalaraman/OpenSpider' },
        ],
        sidebar: [
            {
                text: 'Introduction',
                items: [
                    { text: 'What is OpenSpider?', link: '/' },
                    { text: 'Getting Started', link: '/getting-started' },
                ],
            },
            {
                text: 'Guides',
                items: [
                    { text: 'Configuration', link: '/configuration' },
                    { text: 'Channels (WhatsApp)', link: '/channels' },
                    { text: 'Dashboard', link: '/dashboard' },
                    { text: 'Tools & Skills', link: '/tools-and-skills' },
                ],
            },
            {
                text: 'Reference',
                items: [
                    { text: 'CLI Reference', link: '/cli-reference' },
                    { text: 'Architecture', link: '/architecture' },
                    { text: 'Security', link: '/security' },
                    { text: 'Troubleshooting', link: '/troubleshooting' },
                ],
            },
        ],
        socialLinks: [
            { icon: 'github', link: 'https://github.com/vbalaraman/OpenSpider' },
        ],
        footer: {
            message: 'Built with 🕷️ by the OpenSpider team',
            copyright: '© 2026 OpenSpider',
        },
        search: {
            provider: 'local',
        },
        outline: {
            level: [2, 3],
        },
    },
})

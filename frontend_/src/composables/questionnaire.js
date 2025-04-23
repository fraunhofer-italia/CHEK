export const questions = [
    {
        label: 'How open to changes are internal staff involved in the building permit process?',
        category: 'Internal staff',
        maturity_category: 'Organization',
        count: 0,
        options: [
            'Staff does not express openness to change or digitalization.',
            'Less than 25% of staff acknowledge the need for digital transformation, ad-hoc cooperation on digitalization.',
            '25-50% of staff participate in cross-functional teams to identify digitalization needs and benefits, regular meetings on digital technology opportunities.',
            '50-75% of staff exhibit a proactive mindset about adopting digital innovations, training incorporates adaptability and readiness for new technologies.',
            'Over 75% of staff are open to digitalization, some participate in networks to promote digital innovation, defined processes for cooperation on digital best practices.',
            'Staff constantly seeks new digital innovations to improve operations, knowledge sharing programs across stakeholders to spread digital best practices.'
        ]
    },
    {
        label: 'How does higher management approach organizational changes and digital transformation in the building permit process?',
        category: 'Higher management',
        maturity_category: 'Organization',
        count: 1,
        options: [
            'Management does not express openness to changes or digital transformation.',
            'Management supports the vision but lacks a strategy for utilizing digital processes like BIM and GIS.',
            'Movement to kickstart digital processes (BIM, GIS) is bottom-up, with no clear management plans.',
            'Management recognizes digital innovation (BIM, GIS) as important and supports a top-down implementation approach.',
            'Digital innovations (BIM, GIS) are part of the IT strategy, with a promoted implementation plan at all organizational levels.',
            'Digital innovation planning is fully integrated into strategic planning, with visionary awareness supporting service development.'
        ]
    },
    {
        label: 'How capable is your infrastructure in supporting the digital permitting process?',
        category: 'Infrastructure',
        maturity_category: 'Organization',
        count: 2,
        options: [
            'Hardware/software infrastructure is not capable of supporting required tools.',
            'Less than 20% of infrastructure supports required software, limited pilot software and test servers used by less than 20% of staff.',
            '20-50% of infrastructure supports required software, 20-50% of staff have access to software licenses or installed software, internal network available for file sharing.',
            'Up to 80% of infrastructure supports required software, all core permitting software purchased or installed, redundant servers, cloud backup, common data environment for management of data and files.',
            '100% of hardware can run required software and platforms, all hardware/software for digital permit system are fully implemented.',
            'There are programs for continuous infrastructure upgrades, regular server refreshes, software updates, new feature additions.'
        ]
    },
    {
        label: 'How flexible is the legislative system in creating clear and easily interpretable rules for the building permit process?',
        category: 'Legislative system',
        maturity_category: 'Organization',
        count: 3,
        options: [
            'Not open for changes.',
            'No flexibility for clear and easy-to-interpret rules, but efforts to simplify the process are ongoing.',
            'Few technical requirements are clearly formulated, with more than 50% subject to human interpretation.',
            'Municipal efforts to ensure technical requirements are clearly and directly formulated, reducing subjective interpretation.',
            'More than 50% of regulations under municipal scope have clear, easily interpretable texts, simplifying compliance checks.',
            'Regional or national efforts to minimize subjective interpretability of texts, facilitating rule interpretation and simplifying compliance checks.'
        ]
    },
    {
        label: 'What is the state of your strategy for implementing a data ecosystem in the building permit process?',
        category: 'Strategic objectives for data ecosystem implementation',
        maturity_category: 'Organization',
        count: 4,
        options: [
            'No implementation strategy.',
            'Implementation without a guiding strategy, limited awareness, understanding, and use of tools, processes not integrated, lack of standardized practices.',
            'Implementation strategy has some actionable details, general plan but processes not fully integrated, no formal standardized guidelines.',
            'Implementation strategy includes comprehensive action plans and monitoring, recognizes data ecosystem involves technology, process, and policy improvements.',
            'Vision shared by staff and external stakeholders, organization seeks maximum efficiency and effectiveness, integration of processes using multiple technologies (e.g., BIM-GIS).',
            'Culture of innovation and continuous improvement in data ecosystem practices, organization integrates recent innovative tools (e.g., AI, AR, data spaces).'
        ]
    },
    {
        label: 'How much of your staff is working on BIM, GIS, or other technologies in the building permit process?',
        category: 'Dedicated personnel',
        maturity_category: 'Organization',
        count: 5,
        options: [
            'No staff is dedicated to BIM, GIS, or other technologies.',
            'Up to 20% of staff work part-time on BIM, GIS, or other technologies.',
            'Small team of 3-5 staff dedicated to implementing BIM, GIS, or other technologies within the organization and internal processes.',
            'Multiple teams working full-time with BIM, GIS, or other technologies, each team dedicated to a specific part of the process or data technology, high individual and collective knowledge on digital processes and tools.',
            'Department dedicated to digital data (BIM, GIS, etc.) with internal teams for distinct parts of processes or technologies, high individual and collective knowledge, and encouraged sharing.',
            'Team within the department dedicated to maintaining the quality of processes, data, standards, and guidelines.'
        ]
    },
    {
        label: 'How does your organization handle training, preparation, and support for staff working with BIM, GIS, or other technologies?',
        category: 'Training, preparation and support',
        maturity_category: 'Organization',
        count: 6,
        options: [
            'No training or support.',
            'Lack of dedicated training or support, ad hoc external training, less than 8 hours of training per employee per year.',
            'Documented training requirements, annual training provided as needed, 8-16 hours of training per employee per year.',
            'Training managed to meet competency and performance objectives, regular training provided, 16-24 hours of training per employee per year.',
            'Training plans based on roles and competencies, program uses real work examples, internal support and collaboration with partners, 24-40 hours of training per employee per year.',
            'Training integrated into organizational strategies, on-demand training programs, more than 40 hours average training per employee per year.'
        ]
    },
    {
        label: 'What is the overall knowledge and practical experience (with BIM/GIS) of technicians involved on the steps of the building permit process?',
        category: 'Overall knowledge of technicians',
        maturity_category: 'Organization',
        count: 7,
        options: [
            'No technicians have knowledge or practical experience in data technology.',
            'Less than 25% have basic conceptual knowledge, minimal skills and practical experience.',
            '25-50% have basic knowledge, with low practical skills on the tools.',
            '50-75% of staff regularly use data tools and spatial analysis, tend to pursue formal certifications to expand capabilities.',
            'Over 75% have good working knowledge and practical skills, 20% are experts in BIM, GIS, or other technology.',
            '50% of technicians are experts, possess extensive knowledge and experience, serve as mentors or trainers, and share knowledge to build a strong digital ecosystem competency.'
        ]
    },
    {
        label: 'How is the knowledge of the stakeholders in using data technologies (BIM, GIS, or other) within their participation on building permit process?',
        category: 'Stakeholders\' knowledge',
        maturity_category: 'Organization',
        count: 8,
        options: [
            'None of the stakeholders work with data technologies.',
            'Up to 50% of key stakeholders use basic digital data, no data re-use throughout the process.',
            '50-80% of key stakeholders use digital data such as BIM or GIS, primarily isolated use, minimal interoperability, collaboration, and little communication or data re-use.',
            'More than 80% of key stakeholders use shared data in a digital ecosystem, model data accessible to multiple stakeholders.',
            '100% of key stakeholders use an integrated digital ecosystem, all parties have access to the same source of information through digital data (e.g., BIM-GIS) in their specific domain.',
            'Data fully integrated across all stakeholders and steps, real-time data sharing and collaboration, consistent data throughout the digital ecosystem, metrics on data re-use and value creation.'
        ]
    },
    {
        label: 'How does your organization handle data standards and guidelines in the building permit process?',
        category: 'Data standards and guidelines',
        maturity_category: 'Information',
        count: 0,
        options: [
            'No guidelines or data requirements specification.',
            'Human-readable data requirements as basic guidelines, documentation protocols, or data standards.',
            'Standard-based data requirements with basic guidelines for data standardization, such as training manuals and delivery standards.',
            'Standard-based and machine-readable data requirements, organizational standards aligned with industry standards.',
            'Detailed and comprehensive standard-based and formal data requirements covering geometrical, semantical, structural, syntactical, organizational, and legal aspects, enabling easy interoperability and usability.',
            'Organizational modifications to Model View Definitions and Information Delivery Manuals are balloted for inclusion in industry standards, data standards and guidelines fully integrated into organizational policies.'
        ]
    },
    {
        label: 'How are regulations regarding in the building permit process formatted?',
        category: 'Regulations formats',
        maturity_category: 'Information',
        count: 1,
        options: [
            'Natural language, needing interpretation and referring to several external laws and definitions.',
            'Unambiguous natural language, containing needed definitions and related rules, including exceptions, clear governance level priorities, no reference to customs.',
            'Regulations defined as (semi)formalized language or pseudocode.',
            'Regulations are machine-readable.',
            'Regulations are machine-readable and refer to standardized information, fully parameterized rules integrated across platforms.',
            'Database used as a repository of rules, allowing creation of new rules according to regulatory updates.'
        ]
    },
    {
        label: 'How is the access to regulations needed for the building permit process?',
        category: 'Regulations accessibility',
        maturity_category: 'Information',
        count: 2,
        options: [
            'Normative texts can be consulted only in paper and/or PDF format, same for internal and external stakeholders.',
            'Normative texts can be consulted online according to queries and through a webGIS system associating regulations to zoning areas.',
            'Normative texts can be consulted online according to specific queries in a geographic system, limited integration, and dependencies managed manually.',
            'Validation rule sets formalized with version control, central repository with some real-time updating, web-based portals for external access, data can be imported into checking software directly or via APIs.',
            'Tool allows automated analysis of data contents and compliance checks according to defined rules, automated synchronization and versioning from centralized repository.',
            'Codes available in a machine-readable format, tools support translation of non-translated rules or modification of parameters in existing rules.'
        ]
    }
];

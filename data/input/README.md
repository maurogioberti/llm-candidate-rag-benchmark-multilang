# Dataset: Real CV Records

## Overview

This dataset contains **6 real curriculum vitae (CVs)** from technology professionals who explicitly provided written consent for their personal data to be used in this open-source benchmarking project. The CVs are stored as structured JSON files representing post-processed output from a candidate information extraction pipeline.

**This is NOT synthetic or anonymized data.** All records contain real personally identifiable information (PII) from actual individuals.

## Contents

| File | Candidate | Role | Seniority | Location | Languages |
|------|-----------|------|-----------|----------|-----------|
| `CVJeronimoGarcia.json` | Jerónimo García | Frontend Developer (React/Next.js) | Mid | Spain | Spanish (Native), English (C1) |
| `MauroGioberti_ATS.json` | Mauro Gioberti | Senior Backend .NET Engineer | Senior | Spain | Spanish (Native), English (C1) |
| `DonaldoOruciCV.json` | Donaldo Oruci | Co-Founder & CTO | Senior | Spain (Barcelona) | Albanian (Native), English (C1), Italian, Turkish |
| `Jan Claudiu Crisan CV EN.json` | Jan Claudiu Crisan | Software Engineer | Mid-Senior | Romania | Romanian (Native), English (C1) |
| `Natalia_Gutierrez_QA_Tester.json` | Natalia Soledad Gutierrez | QA Tester (Manual & Automation) | Mid | Spain (Barcelona) | Spanish (Native), English (B1) |
| `Gorosito.json` | Pablo Guillermo Gorosito | Junior QA / Frontend Trainee | Junior | Spain | Spanish (Native) |

## Data Structure

Each JSON file follows a structured schema with the following top-level sections:

- **GeneralInfo**: Candidate metadata (name, title, seniority, years of experience, location, languages, etc.)
- **SkillMatrix**: Technical skills with proficiency levels and evidence excerpts
- **ExperienceTimeline**: Work history with role descriptions, technologies, and achievements
- **Education**: Formal education and certifications
- **Certifications**: Professional certificates and training courses
- **HighlightedProjects**: Notable projects with links and descriptions
- **KeyStrengths**: Summary of core competencies
- **DevelopmentAreas**: Areas for growth or improvement
- **CulturalFit**: Soft skills, collaboration style, and team dynamics
- **HiringRecommendation**: Overall assessment and hiring recommendation
- **CleanedResumeText**: Full-text representation of the CV (contains most PII)

## Privacy & PII Warning

### ⚠️ Personally Identifiable Information (PII)

All files in this dataset contain **real PII**, including but not limited to:

- **Full legal names**
- **Email addresses** (personal Gmail, Hotmail, etc.)
- **Phone numbers** (mobile and international)
- **LinkedIn profile URLs**
- **GitHub profile URLs**
- **Personal website URLs**
- **Exact residential locations** (cities, regions, countries)
- **Dates of birth** (in some cases)
- **Nationality and immigration status**
- **Driver's license information**
- **Educational institution names and dates**
- **Employer names and employment dates**

The `CleanedResumeText` field contains the highest concentration of PII, as it represents the original CV in near-verbatim form.

### Consent & Ethical Use

- All individuals **explicitly consented in writing** to the publication and use of their CVs for open-source research, benchmarking, and demonstration purposes.
- Consent was obtained directly from each candidate prior to inclusion in this repository.
- No anonymization or redaction has been applied to the data.

### Intended Use

This dataset is intended for:

- **Benchmarking** RAG (Retrieval-Augmented Generation) pipelines for candidate search and matching
- **Evaluating** LLM-based question answering systems over structured professional data
- **Testing** multilingual NLP capabilities (Spanish, English, Romanian, Albanian, Italian)
- **Demonstrating** information extraction, structured output generation, and semantic search
- **Academic and research** purposes in AI/ML and NLP domains

### Usage Restrictions & Recommendations

**Do NOT use this dataset for:**

- Production recruitment or hiring decisions
- Commercial candidate databases or talent marketplaces
- Delete or redact **PII** if forking this repository for public-facing demos or tutorials
- Training models for sale or commercial deployment without explicit additional consent
- Any purpose that could harm, misrepresent, or exploit the individuals represented

**Privacy Recommendations:**

- **Use local models** (e.g., Ollama, local LLMs) when experimenting with this data to avoid sending PII to third-party APIs
- **Do not upload** this data to cloud-based LLM services (OpenAI, Anthropic, Google, etc.) unless you have explicit authorization
- **Delete or redact** PII if forking this repository for public-facing demos or tutorials
- **Cite this repository** and acknowledge the contributors if using the data in publications or presentations

## Data Provenance

This dataset was created as part of a **multilingual RAG benchmarking project** comparing .NET (Semantic Kernel) and Python (LangChain) implementations. The CVs were voluntarily submitted by real candidates and processed through an LLM-powered extraction pipeline to generate the structured JSON format.

**Data Collection Date:** 2024–2025  
**Processing Pipeline:** LLM-based information extraction (cloud and local models, depending on experiment configuration)
**Schema Version:** v1.0 (candidate_record.schema.json)

## License & Attribution

This dataset is part of an open-source project licensed under the repository's main license (see top-level LICENSE file). However, the **personal data within the CVs remains the property of the respective individuals** and is shared under their explicit consent for the purposes outlined above.

**If you use this dataset in research, publications, or presentations:**

- Cite this repository
- Acknowledge the voluntary participation of the candidates
- Respect the privacy and consent boundaries outlined in this document

## Contact & Questions

For questions about consent, data removal requests, or ethical use inquiries, please open an issue in the repository or contact the repository maintainer.

---

**Last Updated:** February 2026  
**Dataset Version:** 1.0  
**Total Records:** 6

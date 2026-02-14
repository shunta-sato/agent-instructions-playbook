# References

This playbook is inspired by, or aligned with, the following sources.

## Tooling: how instructions/skills are loaded

### OpenAI Codex
- OpenAI, *Codex — Example: using AGENTS.md and ExecPlan* (planning/handoff pattern): https://cookbook.openai.com/examples/codex/agents_md
- Anthropic, *Claude Code common workflows* (planning and iterative execution): https://docs.anthropic.com/en/docs/claude-code/common-workflows
- AGENTS.md discovery and size cap (`project_doc_max_bytes`): https://developers.openai.com/codex/guides/agents-md/
- Advanced config (includes `project_doc_max_bytes` and related knobs): https://developers.openai.com/codex/config-advanced/
- Skills overview (discovery locations, explicit `$` invocation): https://developers.openai.com/codex/skills/
- Skills format and “only load body when invoked” (progressive disclosure): https://developers.openai.com/codex/skills/create-skill

### GitHub Copilot / VS Code
- Repository custom instructions (`.github/copilot-instructions.md`) and path-specific instructions (`.github/instructions/*.instructions.md`): https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Prompt files (recommended location `.github/prompts/`, run via `/prompt-name` in chat): https://code.visualstudio.com/docs/copilot/customization/prompt-files
- GitHub Docs prompt files (Customization library): https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files
- VS Code Agent Skills (`.github/skills/*/SKILL.md`) and progressive disclosure model: https://code.visualstudio.com/docs/copilot/customization/agent-skills
- VS Code Copilot settings reference (default search locations for instruction/prompt files): https://code.visualstudio.com/docs/copilot/reference/copilot-settings
- GitHub “About Agent Skills” (concepts and supported products): https://docs.github.com/en/copilot/concepts/agents/about-agent-skills

## UI visual verification / snapshot testing

- Nacho Bassino, *Automating UI verification for AI coding agents* (example contract using Make targets and AGENTS flow): https://nachbaur.com/posts/ai-agent-ui-testing/
- Playwright docs, *Visual comparisons / snapshot testing*: https://playwright.dev/docs/test-snapshots
- Point-Free SnapshotTesting (Swift): https://github.com/pointfreeco/swift-snapshot-testing
- CashApp Paparazzi (Android): https://github.com/cashapp/paparazzi
- Roborazzi (Android/Compose screenshot testing): https://github.com/takahirom/roborazzi

## UI/UX core and platform guidance

- ISO 9241 (usability and human-centred design): https://www.iso.org/standard/77520.html
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Nielsen Norman Group, *10 Usability Heuristics for User Interface Design*: https://www.nngroup.com/articles/ten-usability-heuristics/
- Amershi et al., *Guidelines for Human-AI Interaction*: https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/
- Material Design (Android): https://m3.material.io/
- Apple Human Interface Guidelines (iOS): https://developer.apple.com/design/human-interface-guidelines/
- WAI-ARIA Authoring Practices Guide (Web): https://www.w3.org/WAI/ARIA/apg/

## Tone & Manner (トンマナ)

- Canva, *トンマナとは？意味や使い方を理解してデザインに統一感を* (definition including tone as atmosphere and manner as explicit rules): https://www.canva.com/ja_jp/learn/what-is-tone-manner/
- A List Apart, *Style Tiles and How They Work* (visual comparison artifact between mood and full comps): https://alistapart.com/article/style-tiles-and-how-they-work/
- Design Tokens Community Group, *Design Tokens Format Module* (exchange format with `$type` / `$value`): https://www.designtokens.org/TR/2025.10/format/
- Design Tokens Community Group: https://www.designtokens.org/
- Nielsen Norman Group, *Design Systems vs. Style Guides* (consistency context for cross-product execution): https://www.nngroup.com/articles/design-systems-vs-style-guides/

## Readability / Clean code / Architecture

- Dustin Boswell & Trevor Foucher, *The Art of Readable Code* (O’Reilly). (Press release with ISBN): https://www.oreilly.com/pub/pr/2942
- Robert C. Martin, *Clean Code* (Pearson): https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000009044/9780136083252
- Robert C. Martin, *Clean Architecture* (Pearson): https://www.pearson.com/en-us/subject-catalog/p/clean-architecture-a-craftsman-s-guide-to-software-structure-and-design/P200000009528/9780134494326
- Robert C. Martin (Uncle Bob), “The Clean Architecture” (blog, 2012): https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Michael Feathers, *Working Effectively with Legacy Code* (Pearson): https://mitpressbookstore.mit.edu/book/9780131177055
- Bass / Clements / Kazman, *Software Architecture in Practice, 3rd Edition* (SEI/CMU): https://www.sei.cmu.edu/library/software-architecture-in-practice-third-edition/

## Code smells / Anti-patterns

- Martin Fowler — Code Smell: https://martinfowler.com/bliki/CodeSmell.html
- Refactoring.guru — Code Smells catalog: https://refactoring.guru/refactoring/smells
- Martin Fowler — Anemic Domain Model: https://martinfowler.com/bliki/AnemicDomainModel.html
- Foote & Yoder — Big Ball of Mud: https://www.laputan.org/mud/
- Hillside — AntiPatterns book page: https://hillside.net/antipatterns-book

## Requirements / NFR

- ISO/IEC/IEEE 29148:2018 (requirements engineering standard, overview): https://www.iso.org/standard/72089.html
- ISO/IEC 25010 maintainability sub-characteristics (includes “Modularity”): https://www.iso25000.com/index.php/en/iso-25000-standards/iso-25010/57-maintainability
- EARS (Easy Approach to Requirements Syntax):
  - IEEE RE 2009 paper metadata (DOI): https://researchr.org/publication/MavinWHN09
  - Overview by the original author: https://alistairmavin.com/ears/
- INCOSE Requirements WG, “Guide to Writing Requirements” (characteristics excerpts):
  - https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2023/gtwr_introduction_and_concepts_012823.pdf
- https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2023/gtwr_characteristics_section_2_012823.pdf

## Concurrency / Threading / Platform guidance

- Pattern-Oriented Software Architecture, Volume 2 (Schmidt, Stal, Rohnert, Buschmann): https://www.wiley.com/en-us/Pattern-Oriented+Software+Architecture%2C+Volume+2%3A+Patterns+for+Concurrent+and+Networked+Objects-p-9780471606956
- Java Concurrency in Practice (Goetz et al.): https://jcip.net/
- ROS 2 Executors and Callback Groups (rclcpp): https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Executors.html
- ROS 2 Services (sync/async behavior): https://docs.ros.org/en/rolling/Concepts/Services.html
- Android WorkManager overview: https://developer.android.com/topic/libraries/architecture/workmanager
- Android background execution limits (Android 8+): https://developer.android.com/about/versions/oreo/background
- Foreground service restrictions (Android 12+): https://developer.android.com/about/versions/12/foreground-services
- ThreadSanitizer documentation: https://clang.llvm.org/docs/ThreadSanitizer.html
- Clang Thread Safety Analysis: https://clang.llvm.org/docs/ThreadSafetyAnalysis.html

## Observability / Logging

- Google SRE Book, “Monitoring Distributed Systems”: https://sre.google/sre-book/monitoring-distributed-systems/
- OpenTelemetry concepts and signal model: https://opentelemetry.io/docs/concepts/
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- NIST SP 800-92, “Guide to Computer Security Log Management”: https://csrc.nist.gov/publications/detail/sp/800-92/final
- The Twelve-Factor App, “Logs”: https://12factor.net/logs
- ROS 2 Logging (throttling/once-only patterns): https://docs.ros.org/en/rolling/Concepts/Logging.html

## Documentation and static analysis tools

- Doxygen configuration options:
  - `EXTRACT_PRIVATE`, `WARN_IF_UNDOCUMENTED`, `WARN_IF_INCOMPLETE_DOC`, `WARN_NO_PARAMDOC`: https://www.doxygen.nl/manual/config.html
- clang-tidy:
  - `readability-magic-numbers`: https://clang.llvm.org/extra/clang-tidy/checks/readability/magic-numbers.html

## Versioning

- Semantic Versioning 2.0.0: https://semver.org/


## Bug investigation / postmortem / reporting

- Google SRE Workbook — Postmortem Culture: https://sre.google/workbook/postmortem-culture/
- Google SRE Book — Blameless Postmortem: https://sre.google/sre-book/postmortem-culture/
- NIST SP 800-61r2 PDF (Lessons Learned / post-incident activity): https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-61r2.pdf
- Atlassian Postmortem template (includes Five Whys section): https://www.atlassian.com/incident-management/postmortem/templates
- Atlassian 5 Whys analysis template: https://www.atlassian.com/software/confluence/templates/5-whys-analysis
- Jira bug report template (steps/expected/actual/environment): https://www.atlassian.com/en/software/jira/templates/bug-report
- Mozilla bug writing guidelines (steps/expected/actual; facts vs speculations): https://devdoc.net/web/developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines.html

## Constrained code synthesis / staged lowering

- Wen et al., *AscendCraft: Automatic Ascend NPU Kernel Generation via DSL-Guided Transcompilation* (arXiv:2601.22760): https://arxiv.org/abs/2601.22760

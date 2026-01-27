# References

This playbook is inspired by, or aligned with, the following sources.

## Tooling: how instructions/skills are loaded

### OpenAI Codex
- AGENTS.md discovery and size cap (`project_doc_max_bytes`): https://developers.openai.com/codex/guides/agents-md/
- Sample configuration showing the default `project_doc_max_bytes = 32768`: https://developers.openai.com/codex/config-sample
- Skills format and “only load body when invoked” (progressive disclosure): https://developers.openai.com/codex/skills/create-skill

### GitHub Copilot / VS Code
- Repository custom instructions (`.github/copilot-instructions.md`) and path-specific instructions (`.github/instructions/*.instructions.md`): https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot
- Prompt files (`.github/prompts/*.prompt.md`): https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files
- VS Code Agent Skills (`.github/skills/*/SKILL.md`) and progressive disclosure model: https://code.visualstudio.com/docs/copilot/customization/agent-skills
- GitHub “About Agent Skills” (concepts and supported products): https://docs.github.com/copilot/concepts/agents/about-agent-skills

## Readability / Clean code / Architecture

- Dustin Boswell & Trevor Foucher, *The Art of Readable Code* (O’Reilly). (Press release with ISBN): https://www.oreilly.com/pub/pr/2942
- Robert C. Martin, *Clean Code* (Pearson): https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000009044/9780136083252
- Robert C. Martin, *Clean Architecture* (Pearson): https://www.pearson.com/en-us/subject-catalog/p/clean-architecture-a-craftsman-s-guide-to-software-structure-and-design/P200000009528/9780134494326
- Robert C. Martin (Uncle Bob), “The Clean Architecture” (blog, 2012): https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Michael Feathers, *Working Effectively with Legacy Code* (Pearson): https://mitpressbookstore.mit.edu/book/9780131177055
- Bass / Clements / Kazman, *Software Architecture in Practice, 3rd Edition* (SEI/CMU): https://www.sei.cmu.edu/library/software-architecture-in-practice-third-edition/

## Requirements / NFR

- ISO/IEC/IEEE 29148:2018 (requirements engineering standard, overview): https://www.iso.org/standard/72089.html
- ISO/IEC 25010 maintainability sub-characteristics (includes “Modularity”): https://www.iso25000.com/index.php/en/iso-25000-standards/iso-25010/57-maintainability
- EARS (Easy Approach to Requirements Syntax):
  - IEEE RE 2009 paper metadata (DOI): https://researchr.org/publication/MavinWHN09
  - Overview by the original author: https://alistairmavin.com/ears/
- INCOSE Requirements WG, “Guide to Writing Requirements” (characteristics excerpts):
  - https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2023/gtwr_introduction_and_concepts_012823.pdf
  - https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2023/gtwr_characteristics_section_2_012823.pdf

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

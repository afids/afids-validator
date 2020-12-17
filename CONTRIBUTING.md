# Introduction

Contributors (alphabetical last):  Greydon Gilmore, Jason Kai, Tristan Khuen, Jonathan Lau, Patrick Park, Jak Loree-Spacek, Olivia Stanley

Welcome to the AFIDs validator project!
First off, thank you for considering contributing to the AFIDs validator. Following these guidelines helps us to quickly address your issue, assess changes, and help you finalize your pull requests.

**We welcome all contributions from new features, bug fixes, improving documentation, bug triaging, or writing tutorials.**

## Ground Rules

- Ensure all unit tests pass prior to PR submission.
- Create issues for any major changes and enhancements that you wish to make to allow for community discussion.
- Be welcoming to newcomers and respectful of everyone. See the [Python Community Code of Conduct](https://www.python.org/psf/conduct/).
- Label issues and PRs with the appropriate tag found below.

Unsure where to begin contributing to AFIDs? Here are two places to start
- Beginner issues - issues which should only require a few lines of code, and a test or two.
- Help wanted issues - issues which should be a bit more involved than beginner issues.

## Getting started
Seupt instructions for local testing are found in the README.

### Development Setup
**Ensure local repository is up-to-date prior to making changes and/or pushing back to Git. Best practice is to test locally on a new branch, and make a pull request (PR) to pull in new changes**
1. `git checkout master`
2. `git pull`
3. `git checkout -b feature-branch`
4. Make changes on local repository
2. Test changes by running `heroku local`, which will set up the server locally \
_If the migrations folder has been changed, run `python manage.py db upgrade`_
3. Push to git (`git push -u origin feature-branch`) and create a PR if needed
4. Push to heroku `git push heroku master`

### How to label issues
Please use the following labels to help organize your issues and PRs.

API: an (incompatible) API change\
BENCH: changes to the benchmark suite\
BLD: change related to building numpy\
BUG: bug fix\
DEP: deprecate something, or remove a deprecated object\
DEV: development tool or utility\
DOC: documentation\
ENH: enhancement\
MAINT: maintenance commit (refactoring, typos, etc.)\
REV: revert an earlier commit\
STY: style fix (whitespace, PEP8)\
TST: addition or modification of tests\
REL: related to releasing afids_validator\

### How to report a bug
When filing an bug, make sure to answer these four questions:

1. What browser are you using?
2. What did you do?
3. What did you expect to see?
4. What did you see instead?

### Updating Templates
Templates for the validator stored under the `afids-templates` directory. Within this directory, there are sub-folders. Human-based templates are stored under the `human` sub-directory. To add templates to the validator, add them to the appropriate directory under `afids-templates` and create a pull request.

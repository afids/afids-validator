# AFIDs-Validator: An Open-Access, AI-Guided Platform for Learning Anatomical Landmark Placement in Human and Non-Human Primate Neuroimaging

**Authors:** [Author 1]¹, [Author 2]¹, [Author 3]², [Author N]^N
**Affiliations:** ¹[Institution 1], ²[Institution 2]
**Corresponding author:** [Name], [email]
**ORCID:** [0000-0000-0000-0000]

**Article type:** Educational Resource / Methods and Resource Paper
**Intended for:** Special Issue on "Human Neuroimaging Educational Programs and Training Resources," *Aperture Neuro*

**Keywords:** neuroimaging education; anatomical fiducials; spatial normalization; quality control; AI tutoring; large language models; brain atlas; MRI training; open science; accessibility; NiiVue; TemplateFlow

---

## Abstract

Accurate placement of anatomical landmarks on brain MRI is a foundational skill in human neuroimaging — essential for spatial normalization, template-based registration, and quality control across virtually every analysis pipeline. Yet the skill is taught informally, gated behind expert mentorship and desktop software, and no openly accessible, interactive resource exists that teaches it from first principles with quantitative feedback. Here we describe the **AFIDs Validator** (https://validator.afids.io), an open-access web platform that treats quality assurance and active learning as two sides of the same coin. It integrates two components in the browser, with no software to install: (1) an **AI-guided learning mode** that embeds a large language model (LLM) neuroanatomy tutor inside a browser-based MRI viewer (NiiVue), delivering anatomy-first, viewer-context-aware instruction for all 32 Anatomical Fiducials (AFIDs) landmarks; and (2) a multi-template **validation engine** that accepts landmark files and computes per-landmark Euclidean error against expert-annotated reference templates spanning 15 human and 6 macaque brain atlases. Analysis of the reference library shows that, even within the widely interchanged MNI template family, normalized inter-template variability ranges from 0.4 mm (mammillary bodies) to 2.4 mm (temporal horn), and that AC–PC distances span 27.8–31.0 mm — an 11% range that would introduce systematic errors exceeding trained inter-rater variability if templates were mismatched. Quality-control thresholds are empirically grounded in the published AFIDs multi-rater dataset (Taha et al., 2023); we further mine its per-landmark rater-error distributions to calibrate the tutor's feedback to how hard each landmark actually is and to score each learner placement against trained raters. The AFIDs-Validator platform is a scalable, reproducible, and equitable model for neuroanatomy education, and we release all code, reference data, and the tutor's design under an open license.

---

## 1. Introduction: the training gap in neuroimaging neuroanatomy

The past decade has produced a remarkable ecosystem of open-source neuroimaging infrastructure such as preprocessing pipelines (fMRIPrep, Esteban et al., 2019; FSL, Jenkinson et al., 2012), automated image-quality metrics (MRIQC, Esteban et al., 2017), data-sharing platforms (OpenNeuro, Markiewicz et al., 2021), standardized template libraries (TemplateFlow, Ciric et al., 2022), and browser-native viewers (NiiVue, Taylor & Rorden, 2023). These tools have collectively lowered the barrier to reproducible, large-scale analysis. They share a common dependency on accuracy of spatial normalization — the registration of individual brain volumes to a standard reference space — which underpins nearly every downstream result.

Normalization accuracy is routinely assessed by visual inspection or image-similarity metrics, both of which are insensitive to the regionally specific, anatomically interpretable errors that most commonly corrupt group-level analyses. A brain that appears correctly normalized can harbour a 5–8 mm displacement of the anterior commissure that biases parcellation, tractography, and region-of-interest estimates. Landmark-based quality control addresses this directly where precisely defined anatomical landmarks in a normalized image agree with their template positions, normalization is verified anatomically, not just statistically.

Locating the fundus of a sulcus, the tip of a ventricular horn, or the exact crossing of a commissure on a grayscale volume can be difficult, error-prone, and taught clinically commonly through apprenticeship. A trainee typically learns through an expert, placing landmarks, and being corrected in real time. This model produces excellent raters but does not scale and may be scarse to many trainees in lower-resourced settings. Atlas reading and didactic lectures convey where structures are in the abstract but not how to find them on a specific noisy image, and they provide no feedback on whether the learner got it right.

The **Anatomical Fiducials (AFIDs)** protocol was developed as a framework for landmark-based correspondence (Lau et al., 2019). It defines 32 precisely specified landmarks distributed throughout the brain — from commissural midline structures to ventricular tips and sulcal fundi — with explicit operational definitions that minimize placement ambiguity. Original validation demonstrated mean inter-rater Euclidean errors of 1.0–2.5 mm and intraclass correlation coefficients (ICC) exceeding 0.9 for most landmarks after minimal training (Lau et al., 2019). Subsequent multi-cohort validation (Taha et al., 2023) established these reliability benchmarks across 132 subjects, 30 rater sessions, and four imaging datasets, with rater experience spanning medical students with no prior imaging background to neurosurgical residents. The protocol is maintained as an open GitHub organization (https://github.com/afids) comprising the specification, a curated multi-rater dataset, automated localization tools (autoafids), and Python utilities (afids-utils).

Despite this maturity, using AFIDs in practice still requires 3D Slicer, manual placement of 32 landmarks per scan, and access to template reference files and comparison tooling which is a workflow unfamiliar to most incoming trainees. There is no interactive resource for learning landmark placement, and no browser-native way to check a placement against a reference. The gap is in the user-facing infrastructure that would make the AFIDs ecosystem, and the skill it encodes, broadly teachable. In this work, we present the AFIDs Validator, which provides an AI-guided learning mode that teaches landmark placement interactively — with anatomical explanation, quantitative feedback, and no expert supervision — and an instant-feedback validation engine for any AFIDs file against reference templates. Both run in any browser with nothing to install. This paper describes the platform, the pedagogical design of its tutor, the empirical basis for its feedback, and the accessibility choices that let a trainee use it end-to-end.

## 2. Platform overview

The AFIDs Validator is a browser-based web application on a Flask 3.0 / Python 3.11 backend with a React 18 frontend. It is containerized with Docker Compose and deployed via Nginx, supporting both the hosted instance at https://validator.afids.io and self-hosted institutional deployments. All source code is public at https://github.com/afids/afids-validator under GPL-3.0.

Nothing is installed on the user's device: the complete validation and guided-learning workflows run in any modern browser on any operating system. Use requires no account. ORCID OAuth (https://orcid.org) is optionally available for researcher identity, enabling longitudinal tracking of placement performance across sessions; authenticated users may opt in to contribute sessions to an institutional database (PostgreSQL via SQLAlchemy), and no placement data is retained without explicit consent.

The platform accepts two file formats. **FCSV** (Fiducial CSV) is the native export of 3D Slicer's Markups module (Fedorov et al., 2012), the recommended placement tool in the AFIDs protocol. **AFIDs JSON** is a lightweight alternative produced by the `afids-utils` package. Both are validated against the 32-landmark schema, with automatic detection and internal conversion of coordinate convention (RAS vs. LPS).

The two components — learning and validation — are deliberately continuous: a learner trains on the guided mode, then uploads an independent placement to the validation engine and receives the same quantitative feedback used in research quality control. Learning and QC are the same activity viewed at different levels of mastery.

---

## 3. The guided learning mode: an AI tutor inside the MRI viewer

The guided learning mode (`/learn`) is the platform's central pedagogical contribution: a complete, interactive neuroanatomy training workflow for all 32 AFIDs landmarks, in a browser, without installation, institutional affiliation, or expert supervision (Figures 1 and 2). It embeds a NiiVue (Taylor & Rorden, 2023) MRI viewer loaded with the MNI152NLin2009cAsym T1w template from TemplateFlow (Ciric et al., 2022) beside a streaming LLM chat interface, a live coordinate readout, and per-landmark progress tracking.

### 3.1 The learning cycle

Each landmark proceeds through five steps:

1. **Introduction** (LLM, streamed, ≤5 sentences): the structure's anatomical identity and functional significance; its appearance on T1w contrast; the recommended imaging plane; and the single most common placement error.
2. **Placement** (learner): a click in NiiVue records a coordinate in RAS mm.
3. **Computation** (server, <50 ms): Euclidean distance to the template reference, directional offsets, and a quality rating.
4. **Feedback** (LLM, streamed, ≤6 sentences): a one-line verdict; anatomical reasoning about the likely error; directional guidance in anatomical language; and, when relevant, a specific viewer adjustment.
5. **Dialogue** (learner-initiated): free-form Q&A with maintained conversation history.

A learner completing the full set produces a downloadable session report — a per-landmark table of placements, distances, and quality, together with the full tutoring transcript — that serves both as a study artifact and as documentation of proficiency.

### 3.2 Pedagogical design principles

The tutor's behaviour is engineered around a small set of principles from the learning sciences.

**Contextual instruction.** The learner encounters each landmark *in situ* — instruction arrives at the moment of placement, in the same viewer, on the same image they will be evaluated against. Situating learning in the environment of use improves retention and transfer relative to decontextualized atlas study (Lave & Wenger, 1991; Koedinger & Corbett, 2006).

**Active generation before instruction.** The mode gives a brief orientation but withholds full explanation until the learner has attempted a placement. This ordering reflects the "productive failure" framework (Kapur, 2008, 2016; Loibl et al., 2017): learners who struggle with a problem before receiving targeted instruction show superior long-term retention and transfer. A trainee who has tried — and failed — to locate the posterior commissure integrates the subsequent explanation differently than one who merely read it.

**Anatomy-first, coordinates-never.** The tutor's system prompt explicitly forbids giving target coordinates or numerical navigation. This defends against the most common failure mode of LLMs used as anatomical assistants — supplying the coordinate when asked "where is it" — which trains lookup rather than recognition and produces a skill that collapses on individual-subject data with variable anatomy. Feedback instead reasons from anatomy: *"your placement is consistent with the fornix columns, which lie immediately posterior to the anterior commissure at this level"*

**Viewer-context-aware scaffolding.** The NiiVue viewer state at the moment of placement — zoom, image resolution (1 mm or 2 mm isotropic), and contrast window — is captured and included in the feedback request, letting the tutor recommend concrete viewer changes: *"you placed this at low zoom in 2 mm resolution; switching to 1 mm (the RES button) and zooming in would reveal the fine structure here."* This adaptation to the learner's visual environment is often crucial for improving accuracy.

**Scaffolded, protocol-grounded feedback.** Rather than embedding all 32 definitions in every prompt, the tutor is grounded by retrieval-augmented generation (RAG): for each landmark or question, the most relevant AFIDs protocol definitions, key MRI features, and catalogued common mistakes are retrieved from a knowledge store and injected into the model's context. This keeps feedback anchored to the published protocol and reduces the tutor's reliance on unverified parametric knowledge. When the knowledge store is unavailable, retrieval falls back to the curated landmark dictionary shipped with the codebase.

### 3.3 Model-agnostic backend, and a tutor that works for everyone

The tutor speaks the OpenAI-compatible API standard, configurable through environment variables (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`). This supports commercial models (e.g., GPT-4o; Anthropic Claude via a compatible endpoint) and locally hosted open-weight models (e.g., Llama 3, Mistral via Ollama), as well as low-cost hosted providers. Institutions without commercial API access can run a fully functional tutor on local GPU resources. The pedagogical value derives from the structured prompt, RAG grounding, and feedback workflow and not from any single model's capabilities.

Crucially for an educational resource, the tutor is designed so that *no visitor hits a dead end*:

- **Bring your own key.** From an in-page Settings panel, a learner can select a provider and paste their own API key and model. The key is stored **only in the visitor's browser** and forwarded with their requests; it is never persisted or logged server-side. This lets a learner use their preferred model at their own cost, and lets the resource remain available even under heavy use.
- **Shared default.** When a learner provides no key, requests use a shared default model configured by the deployment, so the tutor works out of the box.
- **Graceful fallback.** If no model is reachable at all, the tutor streams the retrieved static reference material for the current landmark instead of an error, and points the learner to Settings — so learning continues even offline or when a key is exhausted.

The active model is surfaced in the interface, and switching between the shared default and a personal key requires no page reload. Responses stream token-by-token to preserve the pace of instructional dialogue.

---

## 4. The validation engine

### 4.1 Per-landmark computation

For each of the 32 landmarks the validator computes:

- **Euclidean distance** from the user coordinate to the template reference (mm);
- **Directional decomposition**: left/right, anterior/posterior, superior/inferior components (mm), suppressing components below 0.5 mm;
- **Quality classification**: excellent (<1 mm), good (1–2 mm), fair (2–4 mm), needs work (≥4 mm).

Session-level statistics across all 32 landmarks are reported: mean error, standard deviation, best- and worst-performing landmarks, and counts within 1 mm and 2 mm.

### 4.2 Empirical grounding of the feedback thresholds

The four-tier classification — the same scale the tutor uses to phrase its verdicts — is anchored to the published AFIDs multi-rater reliability dataset (Taha et al., 2023). That dataset comprises 132 subjects across four cohorts, with 30 rater sessions spanning novice (0 months imaging experience) to expert (≥24 months), accumulating >300 rater-hours and >45,000 Euclidean-distance measurements.

In that dataset, trained raters achieved mean inter-rater errors of 1.0–1.5 mm for most landmarks, with ICC > 0.9 for landmarks including AC, PC, and the mammillary bodies — placing consistently trained raters in the "excellent–good" range. The 2 mm boundary corresponds roughly to the 75th percentile of trained-rater errors, a realistic proficiency target. Errors exceeding 4 mm corresponded to anatomical *confusion* events (e.g., placing on the habenular commissure instead of PC, or the corpus-callosum body instead of the splenium) rather than imprecision. The thresholds therefore discriminate distinct performance phenotypes rather than carving an arbitrary continuum — which is what makes them meaningful as feedback to a learner.

### 4.3 Interactive visualizations

Three complementary Plotly visualizations are generated per session (Figure 4): a **3D scatter** of template and user landmark sets with error-coloured connecting lines (localizing spatial error patterns, e.g., a global lateral shift indicating a convention mismatch); a **ranked error histogram** identifying outlier landmarks for targeted practice; and a **regional radar chart** revealing region-level biases that implicate specific anatomical confusions (e.g., systematic temporal-horn error from confusing the horn lumen with the choroid fissure).

---

## 5. The reference template library

### 5.1 Scope

The reference library contains 21 fully annotated brain atlases — 15 human and 6 macaque — each with all 32 AFIDs landmarks (Figure 3), yielding 480 expert-annotated human and 192 macaque landmark sets (672 in total). All reference FCSV files are version-controlled in the AFIDs GitHub organization and distributed with the validator.

Human templates span the major contemporary standards (Table 1), from MNI305 (Collins et al., 1994) to the 20-µm BigBrain histological atlas (Amunts et al., 2013), with complete coverage of the MNI152 family that serves as the default output space of major pipelines, plus the Parkinson's-optimized PD25 (Xiao et al., 2017). Macaque templates — D99 (Saleem & Logothetis, 2012), INIA19 (Rohlfing et al., 2012), MacaqueMNI, NMTv1.3 and NMTv2.0asym (Jung et al., 2021), and Yerkes19 (Donahue et al., 2016) — support the translational community for which cross-species normalization verification is an increasing priority.

**Table 1. Human brain templates in the AFIDs Validator reference library**

| Template | Primary use | Citation |
|---|---|---|
| MNI152NLin2009cAsym | fMRIPrep default; contemporary standard | Fonov et al., 2011 |
| MNI152NLin2009cSym | Symmetric variant; FreeSurfer normalization | Fonov et al., 2011 |
| MNI152NLin2009bAsym/Sym | Legacy MNI152 2009b variants | Fonov et al., 2011 |
| MNI152NLin6Asym/Sym | FSL standard space; diffusion imaging | Fonov et al., 2009 |
| MNI152Lin | SPM linear normalization | Fonov et al., 2011 |
| MNI305 | Original MNI standard; clinical reference | Collins et al., 1994 |
| Colin27 | High-resolution single-subject MNI template | Holmes et al., 1998 |
| BigBrain | 20-µm isotropic histological atlas | Amunts et al., 2013 |
| fsaverage | FreeSurfer average surface template | Fischl et al., 1999 |
| OASIS30ANTs | Multi-subject aging template (ANTs registration) | Marcus et al., 2007 |
| PD25 | Parkinson's disease cohort template | Xiao et al., 2017 |
| Agile12v2016 | Population template | — |

*The combined rows (MNI152NLin2009bAsym/Sym, MNI152NLin6Asym/Sym) each denote two templates; a 15th human template, MNI2009cAsym — a near-duplicate alias of MNI152NLin2009cAsym — is included in the library but omitted here and from the inter-template analysis (§5.2).*

### 5.2 Inter-template variability is anatomically meaningful

To quantify anatomically meaningful inter-template variability — independent of coordinate-origin differences between spaces — we expressed each template's 32 landmark positions relative to its own AC coordinate, and restricted the comparison to the eight canonical MNI152/MNI305 templates (a directly comparable family, excluding the near-duplicate MNI2009cAsym alias). AC-normalization removes systematic origin offsets while preserving the relative landmark geometry that any registration must recover; restricting to the MNI family isolates the variability that persists even among templates researchers routinely treat as interchangeable, rather than conflating it with the far larger differences of histological (BigBrain) or surface (fsaverage) atlases.

Across the 31 non-AC landmarks and the eight MNI templates, AC-normalized variability ranged from **0.41 ± 0.21 mm** (right mammillary body, RMB) to **2.35 ± 2.09 mm** (left inferior antero-medial temporal horn, LIAMTH), with an overall mean of 1.20 mm (Figure 5, Table 2). The pattern is anatomically interpretable: diencephalic landmarks (the mammillary bodies and intermammillary sulcus) are most consistent (0.41–0.61 mm), reflecting their compact morphology at the diencephalic floor; brainstem, callosal, and cerebellar landmarks are intermediate (~0.7–0.9 mm); and the posterior temporal-horn and posterior lateral-ventricle landmarks are most variable (up to 2.35 mm; maximum pairwise 9.65 mm), consistent with the greater cross-template variability of these thin, CSF-adjacent structures. That the most consistent landmarks (mammillary bodies, ~0.4 mm) sit well within trained inter-rater precision while the most variable exceed it underscores that even MNI-family references are not freely interchangeable for every landmark.

**Table 2. Inter-template variability by neuroanatomical region (AC-normalized, 8 MNI templates)**

| Region | N landmarks | Mean variability (mm) | Max pairwise (mm) |
|---|---|---|---|
| Diencephalic | 4 | 0.57 | 3.67 |
| Callosal | 2 | 0.73 | 3.60 |
| Brainstem | 7 | 0.86 | 3.63 |
| Cerebellar | 1 | 0.89 | 3.65 |
| Commissural | 1 | 1.26 | 3.89 |
| Basal/Frontal | 6 | 1.42 | 8.29 |
| Ventricular | 4 | 1.56 | 6.61 |
| Temporal | 6 | 1.75 | 9.65 |

### 5.3 AC–PC distance reveals the cost of template mismatch

The AC–PC distance varied from **27.8 mm** (MNI152NLin2009bSym) to **31.0 mm** (MNI305) across the eight MNI templates — an 11% range around a 28.7 mm mean (Figure 5A). The modern nonlinear MNI152 variants cluster tightly: MNI152NLin2009cAsym yields 28.1 mm, the 2009b variants 27.8–27.9 mm, and the FSL-standard MNI152NLin6Asym 28.2 mm — all within rater precision, justifying their interchangeable use. By contrast the older linear MNI152Lin (30.3 mm) and the original MNI305 (31.0 mm) diverge by roughly 2–3 mm from the modern nonlinear templates, exceeding the mean inter-rater variability of trained raters for commissural landmarks (Lau et al., 2019) and producing false-positive QC failures if applied to the wrong space. The reference coordinates also reveal a quantifiable left–right asymmetry (e.g., RALTH vs. LALTH 2.85 mm; RVOH vs. LVOH 2.62 mm) consistent with the rightward asymmetry of MNI population templates; because AFIDs measures each hemisphere independently, the validator can detect asymmetric normalization failures invisible to symmetric registration metrics. Together these results give a quantitative argument — assumed but rarely demonstrated — that template-specific references are necessary, not merely convenient, and they anchor the tutor's assertion that "the right answer" depends on the template.

### 5.4 Two kinds of landmark difficulty — and a decade of rater data

The variability above measures how much *reference templates* disagree. A complementary source of difficulty is how much *trained humans* disagree when placing a landmark — the anatomical fiducial localization error (AFLE). The AFIDs multi-rater data release (Taha et al., 2023) makes this directly measurable: it ships, for each subject, the placements of several trained raters alongside a consensus. From the full release (492 rater annotations across all 132 subjects of the four cohorts — the AFIDs-HCP and AFIDs-OASIS healthy adults, the SNSX 7-tesla controls, and the LHSCPD Parkinson's-disease dataset) we computed the per-landmark distribution of rater-to-consensus error (Figure 6A). Median AFLE spans nearly fourfold across landmarks — from **0.37 mm** for the commissures (PC, AC) and ~0.5 mm for the diencephalic landmarks (mammillary bodies, intermammillary sulcus) up to **1.4–1.5 mm** for the temporal-horn landmarks (RIAMTH, LIAMTH) and ~1.2–1.4 mm for the indusium griseum origins (LIGO, RIGO) — with a global median of 0.87 mm (57% of placements within 1 mm, 82% within 2 mm). The distribution is heavy-tailed for *every* landmark: even the commissures, placed to a median of ~0.37 mm, have a mean roughly twice that, reflecting rare gross "confusion events" (e.g., mistaking the habenular commissure for the PC) superimposed on otherwise sub-millimetre precision. This is why the tutor treats a placement beyond the 90th rater percentile as a likely mis-identification rather than mere imprecision.

Rater difficulty and template variability are related but distinct (Figure 6B): across the 31 non-AC landmarks they correlate at **r = 0.66**, so a landmark that is hard for humans tends also to vary across templates, yet neither predicts the other completely — the ventral occipital horns, for example, vary substantially across templates but are placed fairly reliably by raters. A landmark can be hard to *localize* on a single image, hard to *reproduce* across templates, or both, and a learner benefits from knowing which. We found no systematic left–right reliability asymmetry (mean L−R difference in median AFLE = +0.03 mm across the 11 homologous pairs), indicating the protocol yields balanced bilateral definitions rather than a handedness- or convention-driven bias.

**Rater-calibrated feedback and a "you vs. the experts" metric.** These per-landmark distributions are compiled into a reliability prior the platform consumes at run time, with two consequences. First, the tutor's feedback is calibrated to each landmark's real difficulty: rather than judging every placement on one global scale, it knows a 1.2 mm error is *outside* the trained-rater range for the anterior commissure but squarely *within* it — at the median — for the indusium griseum origin, and it praises or corrects accordingly. Second, after each placement the validator reports where the learner falls within the trained-rater distribution for that landmark — a percentile plus a band (better than the typical trained rater, within range, at the edge, or outside) — turning an abstract millimetre value into a meaningful benchmark that also appears in the session report. Because the prior is regenerated from the released placements by a small script, it sharpens automatically as the dataset grows, and — with ORCID-linked opt-in (§2) — the learners' own placements can feed back into it, making the resource a living instrument rather than a static one.

---

## 6. Accessibility, equity, and reproducibility

For an educational resource, being *reachable* is a first-class design requirement, not an afterthought. Three commitments follow.

**Zero-install, no-gatekeeping access.** The entire experience runs client-side in any modern browser; there is no download, no account requirement, and no license. A graduate student with a laptop and an internet connection has the same access to the guided-learning mode as a trainee at a well-resourced imaging centre. The bring-your-own-key design (§3.3) extends this to the AI tutor itself: learners can run the tutor on a shared default, on a free or low-cost hosted model, or on a locally hosted open-weight model — and, when no model is reachable, still receive protocol-grounded static guidance rather than a failure. The intent is that a visitor can complete every task on the site.

**Web accessibility.** The learning interface is built to be usable beyond the mouse-and-monitor default. The streaming tutor pane is an ARIA live region so screen readers announce feedback as it arrives; interactive controls carry text labels; keyboard focus is visible throughout; and informational text meets contrast targets on the dark theme. These are incremental steps toward WCAG conformance rather than a certification claim; known gaps (notably full keyboard-only fiducial placement on the WebGL canvas) are documented in §8 as active work.

**Reproducibility and openness.** All source code, the reference FCSV files, the tutor's system prompt, and the analysis and figure-generation scripts are released under GPL-3.0 (§ Code and Data Availability). The learning template is pulled from TemplateFlow with server-side caching, so the exact image a learner trains on is a versioned, citable artifact; likewise, the rater-reliability prior that calibrates feedback is regenerated by a released script from the public AFIDs data (§5.4, §10.5). Because the platform is model-agnostic and self-hostable, an institution can reproduce the entire tutoring environment — including with a fully local model for privacy-sensitive settings — from the public repository.

---

## 7. Use cases and curriculum integration

**Individual skill development.** A new trainee can complete the full 32-landmark guided workflow in a single 2–3 hour session with no prerequisites, receiving immediate quantitative and anatomical feedback at each step, then upload a first independent FCSV to the validation engine for a session-level summary.

**Workshops and courses.** The browser-based design suits neuroimaging workshops and online courses (e.g., OHBM educational sessions, Neuromatch-style curricula): participants follow along on any device without installation. A two-hour module — 30 minutes guided learning, 60 minutes independent practice, 30 minutes group review of validation reports — can train a cohort of any size.

**Multi-site rater qualification.** Groups beginning multi-site studies can require raters to reach a defined mean error (e.g., <2 mm across all 32 landmarks) on a designated template before contributing data, using the exportable session report as verifiable documentation of qualification — not currently available through any existing open tool.

**Post-normalization quality control.** Labs using fMRIPrep or other pipelines can add AFIDs-based QC as a downstream check: place the 32 landmarks on a normalized image, upload, and flag any landmark exceeding 4 mm for visual inspection, using the radar chart to localize systematic registration failures.

---

## 8. Evaluation framework and future directions

This platform's learning-outcome validation is prospective, not yet complete. The guided mode is engineered from established learning-science principles, but we have not yet measured its effect on learner performance. The ORCID-linked opt-in database is designed to accumulate the longitudinal placement data needed for such studies, and we outline the intended evaluation so that it can be replicated:

- **Pre/post accuracy** on held-out landmarks and templates, comparing guided learning to self-study and to atlas-only instruction;
- **Transfer** from the training template (MNI152NLin2009cAsym T1w) to individual-subject MRI with variable anatomy — the true test of whether recognition, not lookup, was learned;
- **Reliability convergence** (ICC vs. expert consensus) as a function of practice, benchmarked against the trained-rater distribution of Taha et al. (2023);
- **Ablation** of the viewer-context and RAG-grounding components to attribute any effect to specific design choices.

Other known limitations include the guided mode currently uses one template and one contrast (T1w), so it does not yet expose learners to pathological anatomy or acquisition variability; LLM responses may occasionally contain anatomical inaccuracies and should be treated as scaffolding, not authoritative ground truth; English is currently the only supported language; and full keyboard-only placement on the WebGL canvas is not yet implemented. Planned directions include additional templates and contrasts, spaced-repetition review of previously missed landmarks, an instructor view for cohort progress, a REST API and BIDS App wrapper for the validation engine, and localization.

---

## 9. Discussion

Interactive anatomy tools, where they exist, require installation, data download, and expert guidance, limiting their reach. The AFIDs Validator provides the first browser-native, quantitatively graded, and conversationally responsive training resource for neuroimaging landmark placement, developed against the same protocol and reference standards used in research — not a simplified educational proxy. It does not replace hands-on mentorship or deep anatomical training; it is a scalable complement that can train any number of learners in parallel, at any career stage and location, freeing expert time for the cases that need it — and well-designed intelligent tutoring systems have been shown to approach the effectiveness of human tutors (VanLehn, 2011). 

The tutor's anatomy-first constraint targets a specific, reliable failure mode: asked "where is landmark X", an unconstrained LLM will hand over a coordinate — superficially helpful, educationally counterproductive. The architecture described here — RAG grounding in the protocol, a modal response structure (introduction / feedback / dialogue), viewer-context awareness, and the explicit coordinate prohibition — is a transferable template for deploying LLMs in other applied-anatomy education settings, and a reminder that the pedagogy lives in the harness around the model, not the model alone.

**Turning a decade of annotation into a teacher.** A quiet asset of mature open-science efforts is the accumulated record of how experts actually behave — here, tens of thousands of landmark placements gathered over years of AFIDs annotation. We show this record can be re-purposed from a validation artifact into an instrument of instruction: it tells a learner not merely "you were 1.2 mm off" but "1.2 mm is expert-level for *this* landmark, which even trained raters place to only ~1.2 mm" — feedback that is normative rather than absolute, and honest about the anatomy's inherent difficulty. It also surfaces structure invisible in any single session: that landmark difficulty is heavy-tailed (usual sub-millimetre precision punctuated by rare gross confusions, which the tutor learns to flag), that human difficulty and template variability are related but distinct axes a curriculum can address separately, and that the protocol carries no measurable left–right reliability bias. Because the reliability prior is recomputed by a script and the platform can capture new (opt-in, ORCID-linked) placements, the resource is a *living* one: each cohort of learners both benefits from and, in aggregate, extends the normative data — a flywheel between education and dataset growth that is difficult to build in closed tools. More broadly, this suggests a pattern for the field: wherever a community has curated expert annotations, those annotations can seed a calibrated, self-improving tutor, not just a benchmark.

Because the tutor's feedback thresholds are the validation engine's thresholds, and both are grounded in real inter-rater data, a learner is never trained against a proxy standard. Mastery on the learning mode is readiness to do research-grade quality control. Treating the two as a single continuum — rather than an educational tool and a separate QC tool — is, we argue, the platform's core idea.

---

## 10. Methods

### 10.1 Reference template library
All reference FCSV files were generated by expert raters following the AFIDs protocol (https://afids.github.io/afids-protocol/) and version-controlled in the AFIDs GitHub organization. FCSV files encode coordinates in LPS convention (3D Slicer v4.6+); the validator reads the `CoordinateSystem` header and converts to a canonical internal representation. All 21 templates contain all 32 landmarks.

### 10.2 Inter-template variability analysis
The analysis was restricted to the eight canonical MNI152/MNI305 templates (MNI152Lin; MNI152NLin2009bAsym/bSym/cAsym/cSym; MNI152NLin6Asym/6Sym; MNI305), excluding the near-duplicate MNI2009cAsym alias, so that variability is measured within a directly comparable family. AC-normalized coordinates were computed by subtracting each template's AC coordinate from all 32 positions. For each of the 31 non-AC landmarks we computed the cross-template centroid, each template's Euclidean distance from it (mean ± SD), and the maximum pairwise distance. AC–PC distance is the Euclidean norm of the AC-normalized PC coordinate. Analysis used Python 3.11 and NumPy; code is in the repository (`make_figures.py`, `analyze_afids_templates.py`).

### 10.3 Validation engine
Parsing handles FCSV (Markups v4.6+) and AFIDs JSON. Structural validation confirms all 32 labels present, numeric coordinates, and a valid CoordinateSystem header. Per-landmark distance uses NumPy `linalg.norm`; directional components below 0.5 mm are suppressed. Thresholds: excellent <1 mm, good 1–2 mm, fair 2–4 mm, needs work ≥4 mm, calibrated to Taha et al. (2023), and refined per landmark by the rater-reliability prior (§10.5). Visualizations use Plotly 5.x.

### 10.4 Guided learning mode
NiiVue is embedded as a WebGL2 canvas. The MNI152NLin2009cAsym T1w volume is fetched from TemplateFlow's public S3 bucket on first access and cached server-side, at 2 mm (~1.7 MB, default) and 1 mm (~9 MB) isotropic. Placement coordinates are returned in RAS mm via the NiiVue API to the Flask `/learn/check` endpoint. Viewer state (zoom, resolution, contrast window) is captured at placement and included in the feedback request. LLM communication uses the OpenAI-compatible Python SDK (≥1.0) with streaming over chunked HTTP; per-request overrides (`api_key`, `base_url`, `model`) supplied by the client take precedence over the server default, and are neither logged nor persisted. Landmark context is assembled by retrieval-augmented generation over an embedded knowledge store of AFIDs definitions and protocol passages, with fallback to the curated landmark dictionary. Conversation history is maintained client-side; maximum 512 tokens per turn.

### 10.5 Rater-reliability prior
Per-landmark trained-rater reliability was computed from the AFIDs multi-rater release (Taha et al., 2023). For each subject with multiple rater placements, each rater's Euclidean distance to the per-subject consensus (groundtruth) was measured for every landmark — a quantity invariant to FCSV coordinate convention — and aggregated across all four released cohorts (AFIDs-HCP, AFIDs-OASIS, SNSX, and LHSCPD; 492 rater files, 132 subjects) to obtain, per landmark, the median, mean, and 10th/25th/50th/75th/90th percentiles of AFLE. `compute_reliability.py` regenerates this table (`rater_reliability.json`) from any local copy of the released placements. At run time the tutor maps a learner's per-landmark error to a percentile within this distribution and a four-level band (better than typical / within range / edge / outside), injected into the feedback prompt and returned by `/learn/check`; landmarks absent from the prior fall back to the global fixed thresholds.

### 10.6 Platform stack
Flask 3.0 (Python 3.11), SQLAlchemy + PostgreSQL, React 18, ORCID OAuth 2.0, Docker Compose, Nginx. The database stores, per opted-in session: ORCID-linked user ID (nullable), date, selected template, and the 96 landmark coordinate floats. Migrations use Flask-Migrate/Alembic.

---

## Code and Data Availability

All source code, reference FCSV files, the tutor system prompt, and the analysis and figure-generation scripts (`analyze_afids_templates.py`, `make_figures.py`, `compute_reliability.py`, and the derived `rater_reliability.json`) are available at https://github.com/afids/afids-validator under GPL-3.0; Figures 3–6 regenerate deterministically from the released templates and placements. The platform is live at https://validator.afids.io (DOI: 10.5281/zenodo.10694674). The AFIDs multi-rater dataset (Taha et al., 2023) is at https://github.com/afids/afids-data and https://doi.org/10.5281/zenodo.7641532. The AFIDs protocol is at https://afids.github.io/afids-protocol/.

---

## Acknowledgements

We thank the TemplateFlow team for maintaining the public template infrastructure, the NiiVue developers (C. Rorden and J. C. Taylor) for the open-source WebGL2 viewer, and the raters who contributed to the AFIDs multi-rater dataset. [Funding sources TBD.]

---

## Author Contributions

[To be completed per CRediT taxonomy: Conceptualization, Software, Data curation, Formal analysis, Writing – original draft, Writing – review & editing, Supervision, Funding acquisition.]

---

## Competing Interests

The authors declare no competing interests.

---

## References

Amunts, K., Lepage, C., Borgeat, L., Mohlberg, H., Dickscheid, T., Rousseau, M.-É., … & Evans, A. C. (2013). BigBrain: An ultrahigh-resolution 3D human brain model. *Science*, 340(6139), 1472–1475. https://doi.org/10.1126/science.1235381

Ciric, R., Lorenz, R., Thompson, W. H., Goncalves, M., MacNicol, E., Markiewicz, C. J., … & Poldrack, R. A. (2022). TemplateFlow: FAIR-sharing of multi-scale, multi-species brain models. *Nature Methods*, 19, 1568–1571. https://doi.org/10.1038/s41592-022-01681-2

Collins, D. L., Neelin, P., Peters, T. M., & Evans, A. C. (1994). Automatic 3D intersubject registration of MR volumetric data in standardized Talairach space. *Journal of Computer Assisted Tomography*, 18(2), 192–205.

Donahue, C. J., Sotiropoulos, S. N., Jbabdi, S., Hernandez-Fernandez, M., Behrens, T. E., Dyrby, T. B., … & Van Essen, D. C. (2016). Using diffusion tractography to predict cortical connection strength and distance. *Journal of Neuroscience*, 36(25), 6758–6770. https://doi.org/10.1523/JNEUROSCI.0493-16.2016

Esteban, O., Birman, D., Schaer, M., Koyejo, O. O., Poldrack, R. A., & Gorgolewski, K. J. (2017). MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. *PLOS ONE*, 12(9), e0184661. https://doi.org/10.1371/journal.pone.0184661

Esteban, O., Markiewicz, C. J., Blair, R. W., Moodie, C. A., Isik, A. I., Erramuzpe, A., … & Gorgolewski, K. J. (2019). fMRIPrep: A robust preprocessing pipeline for functional MRI. *Nature Methods*, 16, 111–116. https://doi.org/10.1038/s41592-018-0235-4

Fedorov, A., Beichel, R., Kalpathy-Cramer, J., Finet, J., Fillion-Robin, J.-C., Pujol, S., … & Kikinis, R. (2012). 3D Slicer as an image computing platform for the Quantitative Imaging Network. *Magnetic Resonance Imaging*, 30(9), 1323–1341. https://doi.org/10.1016/j.mri.2012.05.001

Fischl, B., Sereno, M. I., & Dale, A. M. (1999). Cortical surface-based analysis: II. Inflation, flattening, and a surface-based coordinate system. *NeuroImage*, 9(2), 195–207. https://doi.org/10.1006/nimg.1998.0396

Fonov, V., Evans, A. C., Botteron, K., Almli, C. R., McKinstry, R. C., Collins, D. L., & Brain Development Cooperative Group. (2011). Unbiased average age-appropriate atlases for pediatric studies. *NeuroImage*, 54(1), 313–327. https://doi.org/10.1016/j.neuroimage.2010.07.033

Fonov, V. S., Evans, A. C., McKinstry, R., Almli, C. R., & Collins, D. L. (2009). Unbiased nonlinear average age-appropriate brain templates from birth to adulthood. *NeuroImage*, 47(Suppl. 1), S102. https://doi.org/10.1016/S1053-8119(09)70884-5

Holmes, C. J., Hoge, R., Collins, L., Woods, R., Toga, A. W., & Evans, A. C. (1998). Enhancement of MR images using registration for signal averaging. *Journal of Computer Assisted Tomography*, 22(2), 324–333.

Jenkinson, M., Beckmann, C. F., Behrens, T. E. J., Woolrich, M. W., & Smith, S. M. (2012). FSL. *NeuroImage*, 62(2), 782–790. https://doi.org/10.1016/j.neuroimage.2011.09.015

Jung, B., Taylor, P. A., Seidlitz, J., Sponheim, C., Perkins, P., Ungerleider, L. G., … & Messinger, A. (2021). A comprehensive macaque fMRI pipeline and hierarchical atlas. *NeuroImage*, 235, 117997. https://doi.org/10.1016/j.neuroimage.2021.117997

Kapur, M. (2008). Productive failure. *Cognition and Instruction*, 26(3), 379–424. https://doi.org/10.1080/07370000802212669

Kapur, M. (2016). Examining productive failure, productive success, unproductive failure, and unproductive success in learning. *Educational Psychologist*, 51(2), 289–299. https://doi.org/10.1080/00461520.2016.1155457

Koedinger, K. R., & Corbett, A. T. (2006). Cognitive tutors: Technology bringing learning sciences to the classroom. In R. K. Sawyer (Ed.), *The Cambridge Handbook of the Learning Sciences* (pp. 61–77). Cambridge University Press.

Lau, J. C., Parrent, A. G., Eng, J., Parrish, T. B., & Peters, T. M. (2019). A framework for evaluating correspondence between brain images using anatomical fiducials. *Human Brain Mapping*, 40(14), 4163–4179. https://doi.org/10.1002/hbm.24693

Lave, J., & Wenger, E. (1991). *Situated Learning: Legitimate Peripheral Participation*. Cambridge University Press. https://doi.org/10.1017/CBO9780511815355

Loibl, K., Roll, I., & Rummel, N. (2017). Towards a theory of when and how problem solving followed by instruction supports learning. *Educational Psychology Review*, 29(4), 693–715. https://doi.org/10.1007/s10648-016-9379-x

Marcus, D. S., Wang, T. H., Parker, J., Csernansky, J. G., Morris, J. C., & Buckner, R. L. (2007). Open access series of imaging studies (OASIS): Cross-sectional MRI data in young, middle aged, nondemented, and demented older adults. *Journal of Cognitive Neuroscience*, 19(9), 1498–1507. https://doi.org/10.1162/jocn.2007.19.9.1498

Markiewicz, C. J., Gorgolewski, K. J., Feingold, F., Blair, R., Halchenko, Y., Miller, E., … & Poldrack, R. A. (2021). The OpenNeuro resource for sharing of neuroscience data. *eLife*, 10, e71774. https://doi.org/10.7554/eLife.71774

Rohlfing, T., Kroenke, C. D., Sullivan, E. V., Dubach, M. F., Bowden, D. M., Grant, K. A., & Pfefferbaum, A. (2012). The INIA19 template and NeuroMaps atlas for primate brain image parcellation and spatial normalization. *Frontiers in Neuroinformatics*, 6, 27. https://doi.org/10.3389/fninf.2012.00027

Saleem, K. S., & Logothetis, N. K. (2012). *A Combined MRI and Histology Atlas of the Rhesus Monkey Brain in Stereotaxic Coordinates* (2nd ed.). Academic Press.

Taha, A., Gilmore, G., Abbass, M., Kai, J., Kuehn, T., Demarco, J., … & Lau, J. C. (2023). Magnetic resonance imaging datasets with anatomical fiducials for quality control and registration. *Scientific Data*, 10, 449. https://doi.org/10.1038/s41597-023-02330-9

Taylor, J. C., & Rorden, C. (2023). NiiVue: A WebGL2 image viewer for neuroimaging. *Aperture Neuro*, 3. https://doi.org/10.52294/001c.77830

VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4), 197–221. https://doi.org/10.1080/00461520.2011.611369

Xiao, Y., Fonov, V., Chakravarty, M. M., Beriault, S., Al Subaie, F., Sadikot, A., … & Collins, D. L. (2017). A dataset of multi-contrast population-averaged brain MRI atlases of a Parkinson's disease cohort. *Data in Brief*, 12, 370–379. https://doi.org/10.1016/j.dib.2017.04.013

---

## Figure Legends

**Figure 1. The guided-learning interface.** Annotated view of the `/learn` mode. Left: a browser-based NiiVue MRI viewer (MNI152NLin2009cAsym T1w) showing a placed fiducial (red) relative to the expert reference (gold) for the anterior commissure, with a live RAS coordinate readout and a viewer toolbar (zoom, resolution, radiological convention, go-to-landmark, place-fiducial). Right: the AI tutor panel streaming an anatomy-first introduction, a quality badge (Euclidean distance + tier), viewer-aware corrective feedback, and free-form dialogue, above a 32-landmark progress tracker. The active model and the bring-your-own-key control (⚙) appear at top right.

**Figure 2. The guided-learning cycle and its design principles.** Each landmark proceeds through five steps — (1) AI introduction; (2) learner placement in the viewer; (3) server-side error computation (<50 ms); (4) anatomy-first AI feedback; (5) free-form dialogue — repeated across all 32 landmarks. The principles governing the tutor are annotated below: productive failure (attempt before full instruction), anatomy-first (never give raw coordinates), viewer-context awareness (feedback adapts to zoom/resolution), and retrieval-augmented grounding in the AFIDs protocol.

**Figure 3. The 32 AFIDs landmarks on the MNI152NLin2009cAsym T1w template.** Sagittal, coronal, and axial maximum-intensity projections of the reference volume with all 32 landmark positions overlaid (RAS mm), coloured by neuroanatomical region; AC and PC labelled for orientation. The set spans the full anterior–posterior, superior–inferior, and left–right extent of the protocol.

**Figure 4. A worked validation report (illustrative session).** Output generated by the validation engine for one placement set (here a synthetic novice session, for illustration). (A) 3D scatter of expert reference (gold) and placed (black) landmarks, connected by lines coloured by error magnitude. (B) Per-landmark Euclidean error, ranked and coloured by quality tier (excellent <1 mm, good 1–2 mm, fair 2–4 mm, needs work ≥4 mm); the two largest errors reflect anatomical-confusion events (splenium vs. callosal body; PC vs. habenular commissure) rather than imprecision. (C) Mean error per neuroanatomical region, localizing systematic biases.

**Figure 5. Even within the MNI family, references differ enough to matter.** Analysis of the eight canonical MNI152/MNI305 templates (excluding the near-duplicate MNI2009cAsym alias). (A) AC–PC distance per template (27.8–31.0 mm; mean 28.7 mm, dashed): the modern nonlinear MNI152 variants cluster tightly, while the linear MNI152Lin and original MNI305 (highlighted) diverge by ~2–3 mm. (B) Per-landmark AC-normalized inter-template variability (mean distance to the cross-template centroid), ranked from the temporal-horn/ventricular landmarks (LIAMTH 2.35 mm) down to the mammillary bodies (RMB 0.41 mm), coloured by region; dotted lines mark the validator's 1 and 2 mm thresholds. (C) Regional-mean variability radar; Temporal and Ventricular regions are most variable, Diencephalic least.

**Figure 6. Trained-rater reliability grounds the tutor's feedback.** Computed from 492 trained-rater annotations across all 132 subjects of the AFIDs multi-rater release (Taha et al., 2023). (A) Per-landmark rater localization error (AFLE), each landmark shown as its median (dot) and interquartile range (bar), ranked from most reliable (PC, AC; median ~0.37 mm) to least (temporal-horn landmarks and indusium griseum origins; median up to ~1.5 mm), coloured by region; dotted lines at 0.5 and 1.0 mm. (B) The two difficulty axes are related but distinct: per-landmark rater median error vs. inter-template variability for the 31 non-AC landmarks (r = 0.66); labelled points illustrate landmarks that diverge from the trend (e.g., the ventral occipital horn RVOH varies across templates yet is placed reliably by raters). The tutor consumes these distributions to calibrate feedback to each landmark's real difficulty and to score each placement against trained raters.
```

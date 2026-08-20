# **AFIDs-Validator: An Open-Access, AI-Guided Platform for Learning Anatomical Landmark Placement**

### **Authors**

### Alaa Taha1,2, Dhananjhay Bansal2, Arun Thurairajah2,6, Jaime Thrower2, Jason Kai2,5, Tristan Kuehn2,3, Greydon Gilmore2,3,4, Mohamad Abbass2,4,6, Ali R. Khan2,3,5,6,7  & Jonathan C. Lau2,3,4,6,7

### **Affiliations** 1\. Stanford University School of Medicine, Stanford, CA, United States of America. 2\. Imaging Research Laboratories, Robarts Research Institute, Western University, London, Canada. 3\. School of Biomedical Engineering, Western University, London, Canada. 4\. Department of Clinical Neurological Sciences, Division of Neurosurgery, Western University, London, Canada. 5\. Department of Medical Biophysics, Schulich School of Medicine and Dentistry, Western University, London, Canada. 6\. Graduate Program in Neuroscience, Western University, London, Canada. 7\. Centre for Functional and Metabolic Mapping, Robarts Research Institute, The University of Western Ontario, London, Canada.

\*corresponding author: Jonathan C. Lau ([jonathan.c.lau@gmail.com](mailto:jonathan.c.lau@gmail.com))

**Keywords:** neuroimaging education; anatomical fiducials; spatial normalization; quality control; AI tutoring; large language models; brain atlas; MRI training; open science

## **Abstract**

Accurate placement of anatomical landmarks is a foundational skill in neuroimaging. Yet it is taught informally through expert mentorship and requires desktop software. There is no openly accessible, interactive resource that teaches it from first principles with quantitative feedback. Here we describe the AFIDs-Validator ([https://validator.afids.io](https://validator.afids.io)), an open-access web platform that integrates quality assurance and active learning in the browser. We present: (1) an AI-guided learning mode that embeds a large language model (LLM) neuroanatomy tutor inside a browser-based MRI viewer (NiiVue), delivering anatomy-first, viewer-context-aware instruction for localization of various brain landmarks; and (2) a multi-template validation engine that accepts landmark files and computes per-landmark Euclidean error against expert-annotated reference templates spanning 15 human and 6 macaque brain atlases. Analysis of 492 expert annotations across 132 subjects shows that landmark difficulty spans nearly fourfold — from a median trained-rater error of 0.37 mm at the commissures to ~1.5 mm at the temporal horns — and is heavy-tailed at every landmark; the platform compiles these distributions into a per-landmark reliability prior so that the same 1.2 mm placement is scored as *expert* on a hard landmark yet *off-target* on an easy one, and each learner is placed within the trained-rater distribution rather than against an arbitrary threshold. We further demonstrate the validation engine catching a real template-space mismatch as an anatomically localized error signature (mean 2.9 mm, concentrated in temporal and ventricular landmarks) that global image-similarity checks miss. The AFIDs-Validator platform is a scalable, reproducible, and equitable model for neuroanatomy education, and we release all code, reference data, and the tutor's design under an open license.

## **1\. Introduction**

The past decade has produced a remarkable ecosystem of open-source neuroimaging infrastructure such as preprocessing pipelines (fMRIPrep, Esteban et al., 2019; FSL, Jenkinson et al., 2012), automated image-quality metrics (MRIQC, Esteban et al., 2017), data-sharing platforms (OpenNeuro, Markiewicz et al., 2021), standardized template libraries (TemplateFlow, Ciric et al., 2022), and browser-native viewers (NiiVue, Taylor & Rorden, 2023). These tools have collectively lowered the barrier to reproducible, large-scale analysis. They share a common dependency on registration accuracy of individual brain volumes to a standard reference space, which underpins nearly every downstream result.

Normalization accuracy is routinely assessed by visual inspection or image-similarity metrics, both of which are insensitive to the regionally specific, anatomically interpretable errors that can corrupt group-level analyses. A brain that may appear correctly normalized can harbor misregistration errors that bias parcellation, tractography, and region-of-interest estimates. Landmark-based quality control addresses this directly where precisely defined anatomical landmarks in a normalized image must agree with their template positions.

Locating the fundus of a sulcus, the tip of a ventricular horn, or the exact crossing of a commissure on a grayscale volume is difficult and error-prone, and the skill is most often taught clinically through apprenticeship. A trainee typically learns through an expert, placing landmarks, and being corrected in real time. This model produces excellent raters but does not scale and may be unavailable to many trainees in lower-resourced settings. Atlas reading and didactic lectures convey where structures are in the abstract but not how to find them on a specific noisy image, and they provide no feedback on whether the learner got it right.

The Anatomical Fiducials (AFIDs) protocol was developed as a framework for landmark-based correspondence (Lau et al., 2019). It defines precisely specified landmarks distributed throughout the brain (from commissural midline structures to ventricular tips and sulcal fundi) with explicit operational definitions that minimize placement ambiguity. Original validation studies demonstrated mean inter-rater Euclidean errors of 1 to 2 mm and intraclass correlation coefficients (ICC) exceeding 0.9 for most landmarks after minimal training (Lau et al., 2019). Subsequent multi-cohort validation (Taha et al., 2023\) established these reliability benchmarks across 132 subjects, 30 rater sessions, and four imaging datasets, with rater experience spanning trainees with no prior imaging background to neurosurgical residents. The protocol is maintained as an open GitHub organization ([https://github.com/afids](https://github.com/afids)) comprising the specification, a curated multi-rater dataset, automated localization tools (autoafids), and Python utilities (afids-utils).

Despite this maturity, using AFIDs in practice still requires 3D Slicer (Fedorov et al., 2012\) and access to template reference files and comparison tooling which is a workflow unfamiliar to most incoming trainees. There is no interactive resource for learning landmark placement, and no browser-native way to check a placement against a reference. The gap is in the user-facing infrastructure that would make the AFIDs ecosystem, and the skill it encodes, broadly teachable. In this work, we present the AFIDs-Validator ([https://validator.afids.io](https://validator.afids.io)), which provides **(1) an AI-guided learning mode** that teaches landmark placement interactively with anatomical explanation, quantitative feedback, and no expert supervision and **(2) an instant-feedback validation engine** for any AFIDs file against reference templates. This paper describes the platform, the pedagogical design of the AI tutor, the empirical basis for its feedback, and the accessibility choices that let a trainee use it end-to-end.

## **2\. Platform overview**

The AFIDs-Validator (see Figure 1\) is a browser-based web application on a Flask 3.0 / Python 3.11 backend with a React 18 frontend. It is containerized with Docker Compose and deployed via Nginx, supporting both the hosted instance at: [validator.afids.io](https://validator.afids.io) and self-hosted institutional deployments. All source code is public at: [github.com/afids/afids-validator](https://github.com/afids/afids-validator) under GPL-3.0.

The complete guided-learning and validation workflows run in any modern browser on any operating system. ORCID OAuth ([https://orcid.org](https://orcid.org)) is optionally available for researcher identity, enabling longitudinal tracking of placement performance across sessions; authenticated users may opt in to contribute sessions to an institutional database (PostgreSQL via SQLAlchemy), and no placement data is retained without explicit consent.

The validator engine accepts two file formats. **FCSV** (Fiducial CSV) is the native export of 3D Slicer's Markups module (Fedorov et al., 2012), the recommended placement tool in the AFIDs protocol. **AFIDs JSON** is a lightweight alternative produced by the `afids-utils` package ([https://github.com/afids/afids-utils](https://github.com/afids/afids-utils)). Both are validated against the landmark schema, with automatic detection and internal conversion of coordinate convention (RAS vs. LPS).

The learning and validation components of the AFIDs-Validator are deliberately continuous where a learner trains on the guided mode, then uploads an independent placement to the validation engine and receives the same quantitative feedback used in research quality control.

## **3\. The guided learning mode**

The guided learning mode (`/learn`) is the platform's central pedagogical contribution. This entails an interactive neuroanatomy training workflow for 32 anatomical landmarks, in a browser, without installation, institutional affiliation, or expert supervision (Figures 2 and 3). It embeds a NiiVue (Taylor & Rorden, 2023\) MRI viewer loaded with the MNI152NLin2009cAsym T1w template from TemplateFlow (Ciric et al., 2022\) beside a streaming LLM chat interface, a live coordinate readout, and per-landmark progress tracking.

Each landmark proceeds through five steps:

1. **Introduction** (LLM, streamed, ≤5 sentences): the structure's anatomical identity and functional significance; its appearance on T1w contrast; the recommended imaging plane; and the single most common placement error.  
2. **Placement** (learner): a click in NiiVue records a coordinate in RAS mm.  
3. **Computation** (server, \<50 ms): Euclidean distance to the template reference, directional offsets, and a quality rating.  
4. **Feedback** (LLM, streamed, ≤6 sentences): a one-line verdict; anatomical reasoning about the likely error; directional guidance in anatomical language; and, when relevant, a specific viewer adjustment.  
5. **Dialogue** (learner-initiated): free-form Q\&A with maintained conversation history.

A learner completing the full set produces a downloadable session report containing a per-landmark table of placements, distances, and quality, together with the full tutoring transcript that serves both as a study artifact and as documentation of proficiency. Well-designed intelligent tutoring systems can approach the effectiveness of one-on-one human tutoring when they pair step-level feedback with sound instructional design (VanLehn, 2011); we accordingly design the tutor's behaviour around a small set of principles from the learning sciences:

1. **Contextual instruction.** The learner encounters each landmark in situ — instruction arrives at the moment of placement, in the same viewer, on the same image they will be evaluated against. Situating learning in the environment of use improves retention and transfer relative to decontextualized atlas study (Lave & Wenger, 1991; Koedinger & Corbett, 2006).  
2. **Active generation before instruction.** The mode gives a brief orientation but withholds full explanation until the learner has attempted a placement. This ordering reflects the "productive failure" framework (Kapur, 2008, 2016; Loibl et al., 2017): learners who struggle with a problem before receiving targeted instruction show superior long-term retention and transfer. A trainee who has tried to locate the posterior commissure integrates the subsequent explanation differently than one who merely read it.  
3. **Anatomy-first, coordinates-never.** The tutor's system prompt explicitly forbids giving target coordinates or numerical navigation. This defends against the most common failure mode of LLMs used as anatomical assistants which trains lookup rather than recognition and produces a skill that collapses on individual-subject data with variable anatomy.  
4. **Viewer-context-aware scaffolding.** The NiiVue viewer state at the moment of placement (e.g., zoom, image resolution, and contrast window) is captured and included in the feedback request, letting the tutor recommend concrete viewer changes: *"you placed this at low zoom in 2 mm resolution; switching to 1 mm (the RES button) and zooming in would reveal the fine structure here"*. This adaptation to the learner's visual environment is often crucial for improving accuracy.  
5. **Scaffolded, protocol-grounded feedback.** Rather than embedding all 32 definitions in every prompt, the tutor is grounded by retrieval-augmented generation (RAG): for each landmark or question, the most relevant AFIDs protocol definitions, key MRI features, and catalogued common mistakes are retrieved from a knowledge store and injected into the model's context. This keeps feedback anchored to the published protocol and reduces the tutor's reliance on unverified parametric knowledge. When the knowledge store is unavailable, retrieval falls back to the curated landmark dictionary shipped with the codebase.

The AI tutor LLM engine is configurable through environment variables (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`). This supports commercial models (e.g., GPT-4o; Anthropic Claude via a compatible endpoint) and locally hosted open-weight models (e.g., Llama 3, Mistral via Ollama), as well as low-cost hosted providers. Institutions without commercial API access can run a fully functional tutor on local GPU resources. The pedagogical value derives from the structured prompt, RAG grounding, and feedback workflow and not from any single model's capabilities.

## **4\. The validation engine**

For each of the 32 landmarks the validator computes:

1. **Euclidean distance** from the user coordinate to the template reference (mm);  
2. **Directional decomposition**: left/right, anterior/posterior, superior/inferior components (mm), suppressing components below 0.5 mm;  
3. **Quality classification**: excellent (\<1 mm), good (1–2 mm), fair (2–4 mm), needs work (≥4 mm).  
   

Session-level statistics across all landmarks are reported: mean error, standard deviation, best- and worst-performing landmarks, and counts within 1 mm and 2 mm. The four-tier quality classification communicated to the user is anchored to the published AFIDs multi-rater reliability dataset (Taha et al., 2023). That dataset comprises 132 subjects across four cohorts, with 30 rater sessions spanning novice (0 months imaging experience) to expert (≥24 months), accumulating \>300 rater-hours and \>45,000 Euclidean-distance measurements. In that dataset, trained raters achieved mean inter-rater errors of 1.0 to 1.5 mm for most landmarks, with ICC \> 0.9 for landmarks including AC, PC, and the mammillary bodies. The 2 mm boundary corresponds to roughly the 82nd percentile of trained-rater errors (§5.1), a realistic proficiency target. Errors exceeding 4 mm corresponded to anatomical confusion events (e.g., placing on the habenular commissure instead of PC, or the corpus-callosum body instead of the splenium) rather than imprecision. The thresholds therefore discriminate distinct performance phenotypes rather than carving an arbitrary continuum, which is what makes them meaningful as feedback to a learner.

Three complementary Plotly visualizations are generated per session (Figure 4): a **3D scatter** of template and user landmark sets with error-coloured connecting lines (localizing spatial error patterns, e.g., a global lateral shift indicating a convention mismatch); a **ranked error histogram** identifying outlier landmarks for targeted practice; and a **regional radar chart** revealing region-level biases that implicate specific anatomical confusions (e.g., systematic temporal-horn error from confusing the horn lumen with the choroid fissure).

The reference library contains 21 fully annotated brain atlases (15 human and 6 macaque) each with all 32 AFIDs landmarks (Figure 3), yielding 480 expert-annotated human and 192 macaque landmarks (672 in total). All reference FCSV files are version-controlled in the AFIDs GitHub organization and distributed with the validator.

All 21 reference templates — 15 human and 6 macaque — are catalogued together in Table 1. The human set spans the major contemporary standards, from MNI305 (Collins et al., 1994\) to the 20-µm BigBrain histological atlas (Amunts et al., 2013), with complete coverage of the MNI152 family that serves as the default output space of major pipelines, plus the Parkinson's-optimized PD25 (Xiao et al., 2017). The six macaque templates are D99 (Saleem & Logothetis, 2012), INIA19 (Rohlfing et al., 2012), MacaqueMNI, NMTv1.3 and NMTv2.0asym (Jung et al., 2021), and Yerkes19 (Donahue et al., 2016).

**Table 1\. Brain templates in the AFIDs-Validator reference library (15 human, 6 macaque; all with the full 32-landmark set)**

| Template | Species | Primary use | Citation |
| :---- | :---- | :---- | :---- |
| MNI152NLin2009cAsym | Human | fMRIPrep default; contemporary standard | Fonov et al., 2011 |
| MNI152NLin2009cSym | Human | Symmetric variant; FreeSurfer normalization | Fonov et al., 2011 |
| MNI2009cAsym | Human | Near-duplicate alias of MNI152NLin2009cAsym | Fonov et al., 2011 |
| MNI152NLin2009bAsym/Sym | Human | Legacy MNI152 2009b variants | Fonov et al., 2011 |
| MNI152NLin6Asym/Sym | Human | FSL standard space; diffusion imaging | Fonov et al., 2009 |
| MNI152Lin | Human | SPM linear normalization | Fonov et al., 2011 |
| MNI305 | Human | Original MNI standard; clinical reference | Collins et al., 1994 |
| Colin27 | Human | High-resolution single-subject MNI template | Holmes et al., 1998 |
| BigBrain | Human | 20-µm isotropic histological atlas | Amunts et al., 2013 |
| fsaverage | Human | FreeSurfer average surface template | Fischl et al., 1999 |
| OASIS30ANTs | Human | Multi-subject aging template (ANTs registration) | Marcus et al., 2007 |
| PD25 | Human | Parkinson's disease cohort template | Xiao et al., 2017 |
| Agile12v2016 | Human | Population template | Taha et al., 2023 |
| D99 | Macaque | Histology-based rhesus stereotaxic atlas | Saleem & Logothetis, 2012 |
| INIA19 | Macaque | Primate parcellation & spatial normalization | Rohlfing et al., 2012 |
| MacaqueMNI | Macaque | Macaque MNI-style population template | — |
| NMTv1.3 | Macaque | NIMH Macaque Template v1.3 | Jung et al., 2021 |
| NMTv2.0asym | Macaque | NIMH Macaque Template v2.0 (asymmetric) | Jung et al., 2021 |
| Yerkes19 | Macaque | Surface-based macaque population template | Donahue et al., 2016 |

## **5\. Analysis of reference data**

The reference library answers two quantitative questions that ground the platform's two contributions. First, *how hard is each landmark to place?* — a difficulty benchmark, computed from 492 expert placements, that tells the guided-learning tutor what a good attempt actually looks like landmark-by-landmark (§5.1–5.2). Second, *can the validation engine catch a real registration error?* — a worked quality-control example on the reference templates themselves (§5.3–5.4). We deliberately foreground these over the descriptive template statistics that motivated earlier versions of this analysis: what matters for a learner is not that references differ in the abstract, but exactly how much difficulty each landmark carries and whether the engine flags a mistake a practitioner would actually make.

### 5.1 A difficulty spectrum for landmark placement

Different landmarks are not equally hard, and the guided-learning mode is only as good as its model of that difficulty. We quantified it directly from the released multi-rater dataset: for every subject with multiple raters, each rater's Euclidean distance to the per-subject consensus — the anatomical fiducial localization error (AFLE), a quantity invariant to coordinate convention — was measured for all 32 landmarks and aggregated across all four cohorts (492 rater files, 132 subjects; Figure 5A).

Median AFLE spans **3.9-fold** across the protocol (Figure 5A). At the easy end sit the commissures (PC **0.37 mm**, AC **0.38 mm**) and the diencephalic floor (mammillary bodies and intermammillary sulcus, \~0.5 mm), compact high-contrast targets. At the hard end sit the temporal-horn landmarks (RIAMTH **1.46 mm**, LIAMTH **1.40 mm**) and the indusium griseum origins (LIGO **1.37 mm**, RIGO **1.24 mm**), thin CSF-adjacent structures with ambiguous boundaries. The global median is **0.87 mm**, with 57% of trained-rater placements within 1 mm and 82% within 2 mm. Critically, the distribution is **heavy-tailed for every landmark**: even the commissures, placed to a median of \~0.37 mm, have a mean roughly 2.2× that, and across landmarks the mean sits 1.4–2.3× the median (Figure 5A, mean markers). These tails are rare gross "confusion events" (e.g., mistaking the habenular commissure for the PC) superimposed on otherwise sub-millimetre precision — which is why the tutor treats a placement beyond a landmark's 90th rater percentile as a likely mis-identification rather than mere imprecision, instead of applying one global tolerance to all 32.

### 5.2 Calibrated, "you vs. the experts" feedback

This spectrum is exactly why a single fixed threshold mis-serves a learner, and the platform replaces it with the empirical per-landmark distribution. The same 1.2 mm placement means opposite things depending on the landmark (Figure 5B): on the anterior commissure it falls *beyond* the trained-rater 90th percentile (\~96th percentile — outside the expert range), whereas on the indusium griseum origin it sits *below* the median (\~42nd percentile — a solidly expert placement). A tutor that praised or corrected both identically would teach the wrong lesson at least once. The reliability prior lets the tutor grade each placement against the raters who defined the landmark, and, after each attempt, the validator reports where the learner falls within that distribution — a percentile plus a four-level band (better than the typical trained rater / within range / at the edge / outside; Figure 5C shows the underlying mm→percentile calibration) — turning an abstract millimetre value into a meaningful "you vs. the experts" benchmark that also appears in the session report. Because the prior is regenerated from the released placements by a small script (§9.5), it sharpens automatically as the dataset grows, and — with ORCID-linked opt-in (§2) — learners' own placements can feed back into it, making the resource a living instrument rather than a static one.

### 5.3 Two kinds of difficulty, and a template caveat

Rater difficulty (how hard a landmark is to *localize* on one image) is related to but distinct from inter-template variability (how much it *moves* across reference templates). Across the 31 non-AC landmarks the two correlate at **r \= 0.66** (Figure 6A): hard-to-localize landmarks tend also to vary across templates, yet neither predicts the other completely — the ventral occipital horns, for instance, vary substantially across templates but are placed reliably by raters. A learner benefits from knowing which kind of difficulty a landmark carries. The reliability itself is balanced bilaterally: the mean left–right difference in median AFLE is only **\+0.03 mm** across the 11 homologous pairs, indicating convention-neutral definitions rather than a handedness bias.

The template-variability axis is a correctness caveat rather than a headline. Expressing each template's landmarks relative to its own AC and restricting to the eight canonical MNI152/MNI305 templates (a directly comparable family), AC-normalized variability ranges from **0.41 mm** (right mammillary body) to **2.35 mm** (left temporal horn), mean 1.20 mm, ranked by region in Figure 6B and Table 2. AC–PC distance spans **27.8–31.0 mm**: the modern nonlinear MNI152 variants cluster within \~28.0 ± 0.2 mm, while the linear MNI152Lin (30.3 mm) and original MNI305 (31.0 mm) diverge by 2–3 mm. The practical consequence is that references are not freely interchangeable for every landmark — which motivates the template-specific reference sets the validator ships, and sets up the worked failure below.

**Table 2\. Inter-template variability by neuroanatomical region (AC-normalized, 8 MNI templates)**

| Region | N landmarks | Mean variability (mm) | Max pairwise (mm) |
| :---- | :---- | :---- | :---- |
| Diencephalic | 4 | 0.57 | 3.67 |
| Callosal | 2 | 0.73 | 3.60 |
| Brainstem | 7 | 0.86 | 3.63 |
| Cerebellar | 1 | 0.89 | 3.65 |
| Commissural | 1 | 1.26 | 3.89 |
| Basal/Frontal | 6 | 1.42 | 8.29 |
| Ventricular | 4 | 1.56 | 6.61 |
| Temporal | 6 | 1.75 | 9.65 |

### 5.4 A worked quality-control catch

The validation engine's purpose is to surface exactly this kind of error on real data, and it is worth showing it work rather than asserting it. We reproduced a common, silent mistake — landmarks defined in one MNI space checked against a reference in another — by validating the MNI305 landmark set against the platform default (MNI152NLin2009cAsym), aligned only at the anterior commissure so that the residual is the geometry a proper registration would still have to recover (Figure 4). The engine does not report a vague "misregistration"; it reports an **anatomically localized signature**: mean error 2.9 mm, with 13 of 32 landmarks beyond their own trained-rater 90th percentile and the error concentrated in the temporal (5.2 mm) and ventricular (4.1 mm) regions while the diencephalic floor stays tight (1.3 mm). The posterior commissure alone lands at 3.6 mm — **4.1× its trained-rater p90** — an unmistakable flag. Crucially, the engine grades severity: repeating the exercise with the milder MNI152Lin mismatch yields a mean of only 1.6 mm with 23 of 32 landmarks still within 2 mm, correctly reading as a subtle rather than gross discrepancy. This region-resolved, per-landmark verdict is precisely what a global image-similarity score or a visual pass would miss, and it is the same output a learner receives on their own upload.

## **6\. Accessibility, equity, and reproducibility**

For an educational resource, being *reachable* is a first-class design requirement, not an afterthought. Three commitments follow:

**Zero-install, no-gatekeeping access.** The entire experience runs in any modern browser with no local installation; there is no download, no account requirement, and no license. A graduate student with a laptop and an internet connection has the same access to the guided-learning mode as a trainee at a well-resourced imaging centre. The bring-your-own-key design (§3) extends this to the AI tutor itself: learners can run the tutor on a shared default, on a free or low-cost hosted model, or on a locally hosted open-weight model — and, when no model is reachable, still receive protocol-grounded static guidance rather than a failure. The intent is that a visitor can complete every task on the site.

**Web accessibility.** The learning interface is built to be usable beyond the mouse-and-monitor default. The streaming tutor pane is an ARIA live region so screen readers announce feedback as it arrives; interactive controls carry text labels; keyboard focus is visible throughout; and informational text meets contrast targets on the dark theme. These are incremental steps toward WCAG conformance rather than a certification claim; known gaps (notably full keyboard-only fiducial placement on the WebGL canvas) are documented in §8 as active work.

**Reproducibility and openness.** All source code, the reference FCSV files, the tutor's system prompt, and the analysis and figure-generation scripts are released under GPL-3.0 (§ Code and Data Availability). The learning template is pulled from TemplateFlow with server-side caching, so the exact image a learner trains on is a versioned, citable artifact; likewise, the rater-reliability prior that calibrates feedback is regenerated by a released script from the public AFIDs data (§5.2, §9.5). Because the platform is model-agnostic and self-hostable, an institution can reproduce the entire tutoring environment — including with a fully local model for privacy-sensitive settings — from the public repository.

## **7\. Use cases and curriculum integration**

The AFIDs-Validator serves as a versatile educational and professional tool, supporting individual skill development through the guided 32-landmark workflow as well as collaborative environments like workshops and neuroimaging courses where participants can interact without complex software installations. Beyond standard anatomical fiducials, the platform's extensible training architecture can be adapted to train raters on specialized landmark types, such as the precise localization of surgical targets for neuromodulation or planning for surgical resection, and can even facilitate the training required for complex image segmentation processes. This flexibility makes the validator an ideal instrument for multi-site rater qualification, allowing research groups to establish rigorous proficiency benchmarks and use exportable session reports as verifiable documentation of a rater's readiness to contribute to high-stakes clinical or research datasets.

## **8\. Evaluation framework and future directions**

This platform's learning-outcome validation is prospective, not yet complete. The guided mode is engineered from established learning-science principles, but we have not yet measured its effect on learner performance. The ORCID-linked opt-in database is designed to accumulate the longitudinal placement data needed for such studies, and we outline the intended evaluation so that it can be replicated:

- **Pre/post accuracy** on held-out landmarks and templates, comparing guided learning to self-study and to atlas-only instruction;  
- **Transfer** from the training template (MNI152NLin2009cAsym T1w) to individual-subject MRI with variable anatomy;  
- **Reliability convergence** (ICC vs. expert consensus) as a function of practice, benchmarked against the trained-rater distribution of Taha et al. (2023);  
- **Ablation** of the viewer-context and RAG-grounding components to attribute any effect to specific design choices.

Other known limitations remain: the guided mode currently uses one template and one contrast (T1w), so it does not yet expose learners to pathological anatomy or acquisition variability. Planned directions include additional templates and contrasts, spaced-repetition review of previously missed landmarks, an instructor view for cohort progress, a REST API and BIDS App wrapper for the validation engine, and localization.

## **9\. Methods**

### 9.1 Reference template library

All reference FCSV files were generated by expert raters following the AFIDs protocol ([https://afids.github.io/afids-protocol/](https://afids.github.io/afids-protocol/)) and version-controlled in the AFIDs GitHub organization. FCSV files encode coordinates in LPS convention (3D Slicer v4.6+); the validator reads the `CoordinateSystem` header and converts to a canonical internal representation. All 21 templates contain all 32 landmarks.

### 9.2 Inter-template variability analysis

The analysis was restricted to the eight canonical MNI152/MNI305 templates (MNI152Lin; MNI152NLin2009bAsym/bSym/cAsym/cSym; MNI152NLin6Asym/6Sym; MNI305), excluding the near-duplicate MNI2009cAsym alias, so that variability is measured within a directly comparable family. AC-normalized coordinates were computed by subtracting each template's AC coordinate from all 32 positions. For each of the 31 non-AC landmarks we computed the cross-template centroid, each template's Euclidean distance from it (mean ± SD), and the maximum pairwise distance. AC–PC distance is the Euclidean norm of the AC-normalized PC coordinate. Analysis used Python 3.11 and NumPy; code is in the repository (`make_figures.py`, `analyze_afids_templates.py`).

### 9.3 Validation engine

Parsing handles FCSV (Markups v4.6+) and AFIDs JSON. Structural validation confirms all 32 labels present, numeric coordinates, and a valid CoordinateSystem header. Per-landmark distance uses NumPy `linalg.norm`; directional components below 0.5 mm are suppressed. Thresholds: excellent \<1 mm, good 1–2 mm, fair 2–4 mm, needs work ≥4 mm, calibrated to Taha et al. (2023), and refined per landmark by the rater-reliability prior (§9.5). Visualizations use Plotly 5.x.

### 9.4 Guided learning mode

NiiVue is embedded as a WebGL2 canvas. The MNI152NLin2009cAsym T1w volume is fetched from TemplateFlow's public S3 bucket on first access and cached server-side, at 2 mm (\~1.7 MB, default) and 1 mm (\~9 MB) isotropic. Placement coordinates are returned in RAS mm via the NiiVue API to the Flask `/learn/check` endpoint. Viewer state (zoom, resolution, contrast window) is captured at placement and included in the feedback request. LLM communication uses the OpenAI-compatible Python SDK (≥1.0) with streaming over chunked HTTP; per-request overrides (`api_key`, `base_url`, `model`) supplied by the client take precedence over the server default, and are neither logged nor persisted. Landmark context is assembled by retrieval-augmented generation over an embedded knowledge store of AFIDs definitions and protocol passages, with fallback to the curated landmark dictionary. Conversation history is maintained client-side; maximum 512 tokens per turn.

### 9.5 Rater-reliability prior

Per-landmark trained-rater reliability was computed from the AFIDs multi-rater release (Taha et al., 2023). For each subject with multiple rater placements, each rater's Euclidean distance to the per-subject consensus (groundtruth) was measured for every landmark — a quantity invariant to FCSV coordinate convention — and aggregated across all four released cohorts (AFIDs-HCP, AFIDs-OASIS, SNSX, and LHSCPD; 492 rater files, 132 subjects) to obtain, per landmark, the median, mean, and 10th/25th/50th/75th/90th percentiles of AFLE. `compute_reliability.py` regenerates this table (`rater_reliability.json`) from any local copy of the released placements. At run time the tutor maps a learner's per-landmark error to a percentile within this distribution and a four-level band (better than typical / within range / edge / outside), injected into the feedback prompt and returned by `/learn/check`; landmarks absent from the prior fall back to the global fixed thresholds.

### 9.6 Platform stack

Flask 3.0 (Python 3.11), SQLAlchemy \+ PostgreSQL, React 18, ORCID OAuth 2.0, Docker Compose, Nginx. The database stores, per opted-in session: ORCID-linked user ID (nullable), date, selected template, and the 96 landmark coordinate floats. Migrations use Flask-Migrate/Alembic.

Code and Data Availability  
All source code, reference FCSV files, the tutor system prompt, and the analysis and figure-generation scripts (`analyze_afids_templates.py`, `make_figures.py`, `compute_reliability.py`, and the derived `rater_reliability.json`) are available at [https://github.com/afids/afids-validator](https://github.com/afids/afids-validator) under GPL-3.0; Figures 3–6 regenerate deterministically from the released templates and placements. The platform is live at [https://validator.afids.io](https://validator.afids.io) (DOI: 10.5281/zenodo.10694674). The AFIDs multi-rater dataset (Taha et al., 2023\) is at [https://github.com/afids/afids-data](https://github.com/afids/afids-data). The AFIDs protocol is at [https://afids.github.io/afids-protocol/](https://afids.github.io/afids-protocol/).

Acknowledgements  
We thank the TemplateFlow team for maintaining the public template infrastructure, the NiiVue developers (C. Rorden and J. C. Taylor) for the open-source WebGL2 viewer, and the raters who contributed to the AFIDs multi-rater dataset. \[Funding sources TBD.\]

Author Contributions  
Following the CRediT taxonomy: **Conceptualization** — J.C.L., A.R.K., A.T., G.G.; **Software** — A.T., J.K., T.K., G.G., J.C.L. (validation engine and reference-template pipeline), A.T. (AI-guided learning mode and rater-reliability calibration), and D.B., A.Th., J.T. (platform development and testing); **Formal analysis** and **Visualization** — A.T.; **Investigation** — D.B., A.Th., J.T.; **Validation** — D.B., A.Th., J.T., M.A., A.T.; **Data curation** — A.T., J.K., T.K., G.G., M.A., A.R.K., J.C.L.; **Writing – original draft** — A.T., J.C.L., A.R.K.; **Writing – review & editing** — all authors; **Supervision** — J.C.L., A.R.K.; **Funding acquisition** — J.C.L., A.R.K. Initials: A.T. (Alaa Taha), D.B. (Dhananjhay Bansal), A.Th. (Arun Thurairajah), J.T. (Jaime Thrower), J.K. (Jason Kai), T.K. (Tristan Kuehn), G.G. (Greydon Gilmore), M.A. (Mohamad Abbass), A.R.K. (Ali R. Khan), J.C.L. (Jonathan C. Lau).

Ethics  
This work is a secondary analysis of previously published, de-identified imaging data; no new human-subjects data were acquired for this study. The reference imaging and multi-rater landmark datasets are from the openly released AFIDs data (Taha et al., 2023), for which ethics approval was obtained from the Human Subject Research Ethics Board (HSREB) at Western University (REB# 109045 and REB# R-17–156), with written informed consent for participation and open data release. The AFIDs-Validator platform records learner-contributed landmark coordinates only with explicit opt-in consent and stores no personally identifying information (§2). *\[If a separate REB determination governs the platform's optional data collection, insert its approval number here.\]*

Competing Interests  
The authors declare no competing interests.

References  
Amunts, K., Lepage, C., Borgeat, L., Mohlberg, H., Dickscheid, T., Rousseau, M.-É., … & Evans, A. C. (2013). BigBrain: An ultrahigh-resolution 3D human brain model. *Science*, 340(6139), 1472–1475. [https://doi.org/10.1126/science.1235381](https://doi.org/10.1126/science.1235381)

Ciric, R., Lorenz, R., Thompson, W. H., Goncalves, M., MacNicol, E., Markiewicz, C. J., … & Poldrack, R. A. (2022). TemplateFlow: FAIR-sharing of multi-scale, multi-species brain models. *Nature Methods*, 19, 1568–1571. [https://doi.org/10.1038/s41592-022-01681-2](https://doi.org/10.1038/s41592-022-01681-2)

Collins, D. L., Neelin, P., Peters, T. M., & Evans, A. C. (1994). Automatic 3D intersubject registration of MR volumetric data in standardized Talairach space. *Journal of Computer Assisted Tomography*, 18(2), 192–205.

Donahue, C. J., Sotiropoulos, S. N., Jbabdi, S., Hernandez-Fernandez, M., Behrens, T. E., Dyrby, T. B., … & Van Essen, D. C. (2016). Using diffusion tractography to predict cortical connection strength and distance. *Journal of Neuroscience*, 36(25), 6758–6770. [https://doi.org/10.1523/JNEUROSCI.0493-16.2016](https://doi.org/10.1523/JNEUROSCI.0493-16.2016)

Esteban, O., Birman, D., Schaer, M., Koyejo, O. O., Poldrack, R. A., & Gorgolewski, K. J. (2017). MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. *PLOS ONE*, 12(9), e0184661. [https://doi.org/10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)

Esteban, O., Markiewicz, C. J., Blair, R. W., Moodie, C. A., Isik, A. I., Erramuzpe, A., … & Gorgolewski, K. J. (2019). fMRIPrep: A robust preprocessing pipeline for functional MRI. *Nature Methods*, 16, 111–116. [https://doi.org/10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)

Fedorov, A., Beichel, R., Kalpathy-Cramer, J., Finet, J., Fillion-Robin, J.-C., Pujol, S., … & Kikinis, R. (2012). 3D Slicer as an image computing platform for the Quantitative Imaging Network. *Magnetic Resonance Imaging*, 30(9), 1323–1341. [https://doi.org/10.1016/j.mri.2012.05.001](https://doi.org/10.1016/j.mri.2012.05.001)

Fischl, B., Sereno, M. I., & Dale, A. M. (1999). Cortical surface-based analysis: II. Inflation, flattening, and a surface-based coordinate system. *NeuroImage*, 9(2), 195–207. [https://doi.org/10.1006/nimg.1998.0396](https://doi.org/10.1006/nimg.1998.0396)

Fonov, V., Evans, A. C., Botteron, K., Almli, C. R., McKinstry, R. C., Collins, D. L., & Brain Development Cooperative Group. (2011). Unbiased average age-appropriate atlases for pediatric studies. *NeuroImage*, 54(1), 313–327. [https://doi.org/10.1016/j.neuroimage.2010.07.033](https://doi.org/10.1016/j.neuroimage.2010.07.033)

Fonov, V. S., Evans, A. C., McKinstry, R., Almli, C. R., & Collins, D. L. (2009). Unbiased nonlinear average age-appropriate brain templates from birth to adulthood. *NeuroImage*, 47(Suppl. 1), S102. [https://doi.org/10.1016/S1053-8119(09)70884-5](https://doi.org/10.1016/S1053-8119\(09\)70884-5)

Holmes, C. J., Hoge, R., Collins, L., Woods, R., Toga, A. W., & Evans, A. C. (1998). Enhancement of MR images using registration for signal averaging. *Journal of Computer Assisted Tomography*, 22(2), 324–333.

Jenkinson, M., Beckmann, C. F., Behrens, T. E. J., Woolrich, M. W., & Smith, S. M. (2012). FSL. *NeuroImage*, 62(2), 782–790. [https://doi.org/10.1016/j.neuroimage.2011.09.015](https://doi.org/10.1016/j.neuroimage.2011.09.015)

Jung, B., Taylor, P. A., Seidlitz, J., Sponheim, C., Perkins, P., Ungerleider, L. G., … & Messinger, A. (2021). A comprehensive macaque fMRI pipeline and hierarchical atlas. *NeuroImage*, 235, 117997\. [https://doi.org/10.1016/j.neuroimage.2021.117997](https://doi.org/10.1016/j.neuroimage.2021.117997)

Kapur, M. (2008). Productive failure. *Cognition and Instruction*, 26(3), 379–424. [https://doi.org/10.1080/07370000802212669](https://doi.org/10.1080/07370000802212669)

Kapur, M. (2016). Examining productive failure, productive success, unproductive failure, and unproductive success in learning. *Educational Psychologist*, 51(2), 289–299. [https://doi.org/10.1080/00461520.2016.1155457](https://doi.org/10.1080/00461520.2016.1155457)

Koedinger, K. R., & Corbett, A. T. (2006). Cognitive tutors: Technology bringing learning sciences to the classroom. In R. K. Sawyer (Ed.), *The Cambridge Handbook of the Learning Sciences* (pp. 61–77). Cambridge University Press.

Lau, J. C., Parrent, A. G., Eng, J., Parrish, T. B., & Peters, T. M. (2019). A framework for evaluating correspondence between brain images using anatomical fiducials. *Human Brain Mapping*, 40(14), 4163–4179. [https://doi.org/10.1002/hbm.24693](https://doi.org/10.1002/hbm.24693)

Lave, J., & Wenger, E. (1991). *Situated Learning: Legitimate Peripheral Participation*. Cambridge University Press. [https://doi.org/10.1017/CBO9780511815355](https://doi.org/10.1017/CBO9780511815355)

Loibl, K., Roll, I., & Rummel, N. (2017). Towards a theory of when and how problem solving followed by instruction supports learning. *Educational Psychology Review*, 29(4), 693–715. [https://doi.org/10.1007/s10648-016-9379-x](https://doi.org/10.1007/s10648-016-9379-x)

Marcus, D. S., Wang, T. H., Parker, J., Csernansky, J. G., Morris, J. C., & Buckner, R. L. (2007). Open access series of imaging studies (OASIS): Cross-sectional MRI data in young, middle aged, nondemented, and demented older adults. *Journal of Cognitive Neuroscience*, 19(9), 1498–1507. [https://doi.org/10.1162/jocn.2007.19.9.1498](https://doi.org/10.1162/jocn.2007.19.9.1498)

Markiewicz, C. J., Gorgolewski, K. J., Feingold, F., Blair, R., Halchenko, Y., Miller, E., … & Poldrack, R. A. (2021). The OpenNeuro resource for sharing of neuroscience data. *eLife*, 10, e71774. [https://doi.org/10.7554/eLife.71774](https://doi.org/10.7554/eLife.71774)

Rohlfing, T., Kroenke, C. D., Sullivan, E. V., Dubach, M. F., Bowden, D. M., Grant, K. A., & Pfefferbaum, A. (2012). The INIA19 template and NeuroMaps atlas for primate brain image parcellation and spatial normalization. *Frontiers in Neuroinformatics*, 6, 27\. [https://doi.org/10.3389/fninf.2012.00027](https://doi.org/10.3389/fninf.2012.00027)

Saleem, K. S., & Logothetis, N. K. (2012). *A Combined MRI and Histology Atlas of the Rhesus Monkey Brain in Stereotaxic Coordinates* (2nd ed.). Academic Press.

Taha, A., Gilmore, G., Abbass, M., Kai, J., Kuehn, T., Demarco, J., … & Lau, J. C. (2023). Magnetic resonance imaging datasets with anatomical fiducials for quality control and registration. *Scientific Data*, 10, 449\. [https://doi.org/10.1038/s41597-023-02330-9](https://doi.org/10.1038/s41597-023-02330-9)

Taylor, J. C., & Rorden, C. (2023). NiiVue: A WebGL2 image viewer for neuroimaging. *Aperture Neuro*, 3\. [https://doi.org/10.52294/001c.77830](https://doi.org/10.52294/001c.77830)

VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4), 197–221. [https://doi.org/10.1080/00461520.2011.611369](https://doi.org/10.1080/00461520.2011.611369)

Xiao, Y., Fonov, V., Chakravarty, M. M., Beriault, S., Al Subaie, F., Sadikot, A., … & Collins, D. L. (2017). A dataset of multi-contrast population-averaged brain MRI atlases of a Parkinson's disease cohort. *Data in Brief*, 12, 370–379. [https://doi.org/10.1016/j.dib.2017.04.013](https://doi.org/10.1016/j.dib.2017.04.013)

Figure Legends  
**Graphical abstract.** The platform in one frame: the live browser interface (left); anatomy-first tutoring; grounding in 492 expert placements across 132 subjects (the per-landmark trained-rater error spectrum); and the calibration idea — the same 1.2 mm placement reads as *expert* on a hard landmark (indusium griseum origin) but *off-target* on an easy one (anterior commissure).

**Figure 1\. The guided-learning interface (live session).** Annotated screenshot of the `/learn` mode running against a local model. ① the browser-based NiiVue MRI viewer (MNI152NLin2009cAsym T1w), here showing a placed fiducial for the anterior commissure across the three orthogonal planes and a 3-D rendering; ② the rater-calibrated result badge reporting Euclidean error and the learner's percentile within the trained-rater distribution for this landmark; ③ the difficulty-aware, anatomy-first AI tutor, whose feedback cites the landmark's real trained-rater difficulty in plain language; ④ the active model and bring-your-own-key control (⚙); ⑤ the 32-landmark progress tracker and session-report export.

**Figure 2\. The guided-learning cycle and its design principles.** Each landmark proceeds through five steps — (1) AI introduction; (2) learner placement in the viewer; (3) server-side error computation (\<50 ms); (4) anatomy-first AI feedback; (5) free-form dialogue — repeated across all 32 landmarks. The principles governing the tutor are annotated below: productive failure (attempt before full instruction), anatomy-first (never give raw coordinates), viewer-context awareness (feedback adapts to zoom/resolution), and retrieval-augmented grounding in the AFIDs protocol.

**Figure 3\. A field guide to the 32 AFIDs landmarks on the MNI152NLin2009cAsym T1w template.** Each panel is a 40 mm patch of the template centred on one landmark, with a crosshair marking the exact point, grouped and coloured by neuroanatomical region. The chip in each panel gives that landmark's median trained-rater localization error (AFLE) and the corner tag its viewing plane (sag = sagittal, used for midline landmarks; ax = axial, for bilateral landmarks). Structure by structure, the guide shows what each landmark actually looks like on the image a learner places it on.

**Figure 4\. A worked quality-control catch on real reference data.** The validation engine run on a genuine template-space mismatch: the MNI305 landmark set validated against the platform default (MNI152NLin2009cAsym), aligned only at the anterior commissure so that the residual is the geometry a proper registration must recover. (A) 3D scatter of the default reference (gold) and the uploaded MNI305 landmarks (black), connected by lines coloured by error magnitude. (B) Per-landmark Euclidean error, ranked and coloured by quality tier (excellent \<1 mm, good 1–2 mm, fair 2–4 mm, needs work ≥4 mm); black ticks mark each landmark's trained-rater 90th percentile — the error exceeds it for 13 of 32 landmarks (mean 2.9 mm), most dramatically at the posterior commissure (3.6 mm, 4.1× its rater p90). (C) Mean error per neuroanatomical region: the signature is localized to the temporal and ventricular landmarks while the diencephalic floor stays tight — exactly what a global similarity score would miss.

**Figure 5\. How hard is each landmark? A difficulty benchmark from 492 expert placements.** Computed from 492 trained-rater annotations across all 132 subjects of the AFIDs multi-rater release (Taha et al., 2023). (A) Per-landmark trained-rater localization error (AFLE), each landmark shown as its median (dot), interquartile range (bar), and mean (×), ranked from most reliable (PC, AC; median \~0.37 mm) to least (temporal-horn landmarks and indusium griseum origins; median up to \~1.5 mm) — a 3.9-fold spread; the mean sitting right of the median at every landmark shows the heavy tail. (B) The same 1.2 mm placement, two verdicts: read against each landmark's trained-rater distribution, 1.2 mm is beyond the 90th percentile for the anterior commissure (outside the expert range) but near the median for the indusium griseum origin (a solidly expert placement). (C) The underlying calibration the platform applies — the mm→percentile mapping for an easy (AC), typical (IMS), and hard (LIGO) landmark; a single error maps to sharply different percentiles.

**Figure 6\. Two distinct kinds of difficulty.** (A) Per-landmark trained-rater median error ("localize") vs. inter-template variability ("reproduce") for the 31 non-AC landmarks (r \= 0.66): related but distinct, with labelled points that diverge from the trend (e.g., the ventral occipital horn RVOH varies across templates yet is placed reliably by raters). (B) Per-landmark AC-normalized inter-template variability across the eight canonical MNI152/MNI305 templates (mean distance to the cross-template centroid), ranked from the temporal-horn/ventricular landmarks (LIAMTH 2.35 mm) down to the mammillary bodies (RMB 0.41 mm), coloured by region; dotted lines mark the validator's 1 and 2 mm thresholds.


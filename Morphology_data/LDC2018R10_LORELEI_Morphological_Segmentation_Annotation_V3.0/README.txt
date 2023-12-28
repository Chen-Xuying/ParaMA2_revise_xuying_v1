                LORELEI Morphological Segmentation Annotation
                                 LDC2018R10
                                Version V3.0
                          Linguistic Data Consortium
                                November 18, 2019

0. What's new in this release

This V3.0 release includes quality control (QC) corrections and
annotations for all languages.  Details on the corrections made are in
section 1.4 below.

This release also includes additional annotation for the manual
identification of root segments for 7 of the 9 languages.  Details on
the inclusion of roots are below in section 1.2 and in the section 1.4
subsection for each language.

This release does not include the supplementary data directory for
Hindi (which for V2.0 had been in the following directory:
data/hin/supplementary_data/).  The supplementary data is no longer
necessary, due to the QC changes in transliteration for Hindi and the
revised columns in the Hindi annotation file, which provide
segmentation annotation for Hindi that matches the version of the
transliterator that is included in the LORELEI Hindi language pack.
Details are in sections 1.4.3 and 3.1 below.

A small number of tokens that had been included in previous releases
were rejected by quality control annotators as out of language or
otherwise unannotatable.  These tokens were removed from the data and
are not included in this release.  Details on which tokens were
removed are included below in section 1.4 under the subsection for
each language.

1. Introduction

This data set provides reference annotation for morphological
segmentation of 9 LORELEI Representative Languages (RLs).  This
annotation will support the development of unsupervised morphological
segmenters and analyzers.

This distribution is limited to Mitch Marcus and his team at the
University of Pennsylvania.  The reference annotations in this data
set will be distributed with the next incremental release of the LRLP
for each of the 9 RLs.

Contents in this data set are described below. 

1.1 Summary of Data Included in this Release

This release includes approximately 2000 tokens from each of 9 RLs,
annotated in isolation for morphological segmentation, along with
annotation for root segment identification for 7 of the 9 RLs.  This
release also includes a concordance for each RL of the location of
every instance of each token string that was annotated, in the 25Kw
situational awareness annotation set of source data for that language.

Languages in non-Latin scripts were annotated in transliteration.

The languages annotated, their language IDs, whether they were
annotated in transliteration (y) or not (n), and whether the root
segments were identified (y) or not (n) are listed below:

Language        ID      Transliteration Roots
Akan            aka     n               n
Hindi           hin     y               y
Hungarian       hun     n               y
Indonesian      ind     n               y
Russian         rus     y               y
Spanish         spa     n               y
Swahili         swa     n               y
Tagalog         tgl     n               y
Tamil           tam     y               n

1.2 Annotation

LDC developed annotation guidelines for this task that apply the
principles of morphological segmentation annotation that were
developed by the University of Pennsylvania team under Mitch
Marcus. Language-independent principled specifications suitable for
use by annotators were developed, and appropriate language-specific
morphological paradigms and other specifications for each target
language were included in an Appendix for each language.

The language-independent guidelines are included in this release here:
docs/Morphological_Segmentation_Guidelines_V1.3.pdf

The language-specific appendices are included in this release here:
docs/Morphological_Segmentation_Appendix_{lang}.pdf

Root segments were also manually identified for 7 of the 9 languages.
Annotators performed root identification by selecting the already
annotated segment that carries the basic meaning of the word.  Due to
the experimental of nature root segment identification combined with
resource constraints, annotators did not receive training specific to
linguistic or morphological roots, and rather followed their own
understanding of the basic meaning of the word to identify the segment
that carries that meaning.

1.3 Data Selection

The languages for morphological segmentation annotation were selected
based on criteria targeting the annotation of a variety of linguistic
features and language types across the 9 annotated languages.

LDC developed token selection criteria and procedures in consultation
with the University of Pennsylvania Marcus team that allowed the
annotation of representative tokens from each targeted language, and
performed human annotation of each selected token.  Approximately 3000
tokens were selected via an automatic procedure in each targeted
language.  Out of this pool of candidate tokens for annotation,
approximately 2000 tokens were manually annotated in each targeted
language.  Tokens not suitable for annotation were manually excluded.

Tokens from non-Latin script languages were transliterated using the
transliterator provided in the LRLP for that language, and the manual
annotation was performed on the transliterated tokens.

1.4 Quality Control Annotation and Corrections

Quality control annotation was performed on all 9 languages.  Several
initial correction passes were applied to all languages equally.
However, because the issues and annotators for each language varied,
the targeted corrections were tailored specifically for each language.
The quality control annotation methods and corrections are described
in this section.

1.4.1 Corrections applied to all 9 languages

1.4.1.1 Pre-annotation

Specific inconsistencies that had been pointed out by the Penn CIS
Marcus team were flagged for manual review.

Instances of extra white space in the annotation were identified and
corrected.

aka_morph-segmentation.tab:n'ano        n'  ano
hun_morph-segmentation.tab:májgyulladást    máj  gyullad ás t
spa_morph-segmentation.tab:sediciosos       sedici os  o s
tgl_morph-segmentation.tab:dayuhan          day<u>  han
tgl_morph-segmentation.tab:katatagpuan      ka ta  tagp<u> an
tgl_morph-segmentation.tab:mamu<U+00AD>lat   ma mu-lat
tgl_morph-segmentation.tab:sisihin    sisi  hin
tgl_morph-segmentation.tab:siya’y  siya ’y

Character mismatches between source token and segmentation were
identified and corrected:

Spanish:
denunció ddenunció
explicó exlicó
extradición exradición
procuración prouración
retractó reractó

Tagalog:
mamu<U+00AD>lat   ma mu-lat
siya’y  siya ’y

A manual review of annotation to flag errors was performed.  Similar
strings with different segmentation were flagged for manual review by
annotators.  A histogram of the most commonly annotated segments for
each language was created, and those segments in the annotation were
examined to identify variations that were flagged for manual review by
annotators.

Hindi transliterator: For this QC annotation, we ran the released
version of the CASL Hindi transliterator (from the LORELEI RL Language
Pack for Hindi) on the source tokens in this corpus.  A discrepancy
between the output created and the expected documented output was
noted, and is described below in section 1.4.3.

1.4.1.2 During annotation

A small number of tokens were rejected by annotators in this round as
out of language or otherwise unannotatable.  These tokens were removed
from the corpus, both from the annotation files and also from the
concordance files.  Details on which tokens were removed are in the
subsections on each language below.

Annotators who worked on quality control corrections were trained on
the goals of the correction and QC task, with an emphasis on
consistency.  Annotators were also lightly trained on the annotation
guidelines for the morphological segmentation task (including the
language-specific appendix for their language).  Annotators completed
a brief practice set that was reviewed by LDC supervisors, and
annotators worked directly with LDC supervisors on the task of
reviewing the annotation as a whole and correcting tokens that had
been flagged as in section 1.4.1.1 for manual review.

For 7 of the 9 languages, annotators were also asked to manually
identify root segments for the annotated tokens.  Annotators performed
root identification by selecting the already annotated segment that
carries the basic meaning of the word.  Due to the experimental nature
root segment identification combined with resource constraints,
annotators did not receive training specific to linguistic or
morphological roots, and rather followed their own understanding of
the basic meaning of the word to identify the segment that carries
that meaning.

1.4.1.3 Post-annotation

Annotation files including segmentation and root segment
identification were created as tab separated files, one for each
language: {lang}_morph-segmentation.tab

Spurious white space was removed, including leading/trailing spaces,
more than one single space, tabs, etc.

Source tokens and segmented tokens were compared to ensure character
integrity.

For non-Latin scripts, a character histogram was created to confirm
that all tokens were in the target script.

Tokens that had been rejected by annotators as out of language or
otherwise unannotatable were removed from concordances.

1.4.2 Akan

All tokens reviewed
351 tokens changed

Tokens rejected by annotator and removed from the corpus:
kuluulu
Nomenyo
yɛerte

1.4.3 Hindi

All tokens reviewed
225 tokens changed
Root segments identified

Transliteration:

The Hindi annotation in this release is consistent with the released
Hindi transliterator in the LORELEI Representative Language Pack for
Hindi.

However, during this QC pass we noted a discrepancy between the output
created by the transliterator and the expected documented output.  The
released transliterator rendered both the aspirated and unaspirated
voiceless affricates (च and छ) as 'chh'.  For this QC annotation, we
manually changed 129 instances in 129 tokens of 'chh' to the expected
'ch' when corresponding to the unaspirated one (च).  Uncorrected
transliteration is transliteration_1 and corrected transliteration is
transliteration_2 in the annotation file
(data/hin/hin_morph-segmentation.tab).

QC annotation was done on the corrected tokens.  Segmentation
annotation and root segmentation identification are provided for both
the uncorrected transliteration (as generated by the released Hindi
transliterator) and also for the corrected transliteration, since that
is more expected and documented output.  Segmentation and roots based
on uncorrected transliteration have trans1 in the name; segmentation
and roots based on corrected transliteration have trans2 in the name.

Prefixes from Sanskrit portion of lexicon (aa-, ati-, apa-, ud-, upa-,
pra-, etc.) were split off for this segmentation annotation.

Derivational processes with only insertion in transliteration were not
annotated as morphological changes, and any such brackets from
previous versions were removed, e.g., itihaas ~ aitihaasik (“history”
~ “historical”) now "aitihaas ik" and not "<ai>tihaas ik”.

Verbs derived by vowel and consonant changes now have changes
explicitly marked, e.g., tor “break (transitive)” <- tuut “break
(intransitive)” now done as t<o><r> and not tor.

Root segments:

Clitics: For cliticized pronoun + postposition, the pronoun is
selected as the root segment.

Compounds: The semantic head was selected as the root segment. For
copulative compounds (e.g., jaanmaal, dakshinapuurvii, naamonishaan)
and others: default to rightmost annotated non-affix segment. For
vaalaa constructions (e.g., tattuuvaalaa), vaalaa selected as root.

1.4.4 Hungarian

All tokens reviewed
212 tokens changed
Root segments identified

Note that the Hungarian annotator pointed out that roots do not always
match segmentation.  In some cases, substrings of an annotated segment
(szava i t vs. sza) are the root, in a few cases superstrings of
segments (mér föld re vs. mérföldre), and some where both substring
and superstring are required (szék lett te vs. széklet).  

Compounds: Annotated in this corpus with two segments as roots (e.g.,
avar + tűz). 

In addition, the root is sometimes abstracted away from surface form
(ere jű has the root erő).

Tokens rejected by annotator and removed from the corpus:
All
Csütör
dolt
ellákban
Hagibis
jú
retard
sér
talkon
valmi

Token removed for punctuation:
könnyű,1

1.4.5 Indonesian

86 tokens corrected
Root segments identified

Root segment identification for reduplicated segments: Either segment
was permitted, although in practice usually the non-capitalized
segment was selected.

1.4.6 Russian

All tokens reviewed
1013 tokens corrected
Root segments identified

Some roots contain two or more segments. 

Token removed from corpus (contains Latin character):
одновpеменно

1.4.7 Spanish

All tokens reviewed
266 tokens corrected
Root segments identified

Brackets occurring in affixes were removed (per Marcus team note on
Spanish data).

1.4.8 Swahili

All tokens reviewed
434 tokens corrected
Root segments identified

Corrections for Swahili focussed primarily on verbs since those were
pointed out by the Marcus team.

Root segment identification is probably better for verbs than for
other categories.

For purely grammatical words (noun class marker + pronoun), the
default was to select the pronoun.

In identifying root segments, the annotator sometimes suggested
strings that were not segments; on those cases the segment that seemed
to best fit was selected.

Tokens rejected by annotator and removed from corpus:
kutamausha
kutumiliwa

1.4.9 Tagalog

47 tokens corrected
Root segments identified

Root segment identification: Annotator was instructed to pick any
reduplicated segement in the case of fully reduplicated segments.

For infixation, both segments were selected, e.g., b um ili. 

There were numerous cases of compounds which have two roots as
well. These are not explicitly marked as any different from infixes.

Tokens rejected by annotator and removed from corpus:
ahesnya
baygo
Hinatuan
pinakamamaking

Tokens removed from corpus due to punctuation:
ari-arian.Tectonic
ka-ulop,kamusta

1.4.10 Tamil

All tokens reviewed
984 tokens corrected

2. Directory Structure

In addition to this README file, the top-level contains the following
structure:

   data/ -- annotation directories
   docs/ -- annotation guidelines and appendices

The data/ directory contains a separate directory for each of the
language IDs (aka, hin, hun, ind, rus, spa, swa, tam, tgl).  

Each of the language directories contains two tab delimited files: the
morphological segmentation annotation ({lang}_morph-segmentation.tab)
and the concordance ({lang}_concordance.tab).

3. Data Formats

The annotation of tokens and the concordance of token string locations
are each presented in a tab delimited file.

3.1 Morphological Segmentation Annotation Files

The annotation file name begins with the language ID:
{lang}_morph-segmentation.tab.  The file consists of two tab delimited
columns for languages that are not annotated in transliteration: token,
segmentation.  The file consists of three tab delimited columns for
languages that are annotated in transliteration: token,
transliteration, segmentation.

The columns in the {lang}_morph-segmentation.tab files include
(however, see below for Hindi):

1. token (word being annotated)
2. transliteration (transliteration using LRLP package transliterator, 
                    included only for languages with transliteration)
3. segmentation (manual annotation according to the annotation guidelines)
4. root (manually identified root segment, included only for languages 
         with root segments identified)

The languages annotated, their language IDs, whether they were
annotated in transliteration (y) or not (n), and whether the root
segments were identified (y) or not (n) are listed below:

Language	ID	Transliteration	Roots
Akan		aka	n		n
Hindi		hin	y		y
Hungarian	hun	n		y
Indonesian	ind	n		y
Russian		rus 	y		y
Spanish		spa	n		y
Swahili		swa	n		y
Tagalog		tgl	n		y
Tamil		tam	y		n

Note that the annotation file for Hindi includes additional columns,
as follows:

1. token (word being annotated)
2. transliteration-1 (transliteration using released version of the 
                      Hindi LRLP package transliterator, which includes 
                      "chh" errors)
3. transliteration-2 (transliteration using the released Hindi LRLP 
                      package transliterator, with the "chh" errors 
                      manually corrected for this release)
4. segmentation_trans1 (manual annotation according to the annotation 
                        guidelines, segments based on transliteration-1)
5. segmentation_trans2 (manual annotation according to the annotation 
                        guidelines, segments based on transliteration-2)
6. root_trans1 (manually identified root segment, segments based on 
                transliteration-1)
7. root_trans2 (manually identified root segment, segments based on 
                transliteration-2)

The difference between transliteration-1 and transliteration-2 is
described above in section 1.4.3.  For complete consistency with the
LRLP Hindi transliterator output, transliteration-1 (and _trans1)
fields should be used.  For the more commonly expected treatment of
"chh" in human transliteration, transliteration-2 (and _trans2) should
be used.  Both are provided in the Hindi annotation file as above.

3.2 Concordance Files

The concordance file name also begins with the language ID:
{lang}_concordance.tab.  The file consists of five tab delimited
columns: doc_id, token_id, token, start_offset, end_offset.  The
source files can be found in the LRLP source data release for each
language.  For each annotated token, the concordance consists of every
occurrence of that token string that appears in a 25Kw set of the
source data that is multiply annotated for LORELEI (the "situational
awareness" set).

Notes on the concordance files:

- The annotation of the tokens is done in isolation (not in the
  context of full document text), and the concordance will therefore
  include tokens that may appear in a different context from the token
  that was annotated.  It is therefore the case that not every
  instance of the token in the concordance would necessarily have the
  same morphological analysis as the annotated token.

- Exact match tokens only are included, including exact match on
  capitalization, diacritics, and other orthographic variants.

- The concordance covers only the 25Kw situational awareness
  annotation set of documents (i.e., it does not cover the full
  monolingual text set).

The columns in the {lang}_concordance.tab files include:

1. doc_id (source file document ID)
2. token_id (token_id from the LTF file for the doc_id)
3. token (identical to word annotated in morph-segmentation files)
4. start_offset (from the LTF file)
5. end_offset (from the LTF file)


---------------------- 
README created by Ann Bies on May 10, 2018
Updated by Ann Bies on September 5, 2018
Updated by Ann Bies on November 18, 2019

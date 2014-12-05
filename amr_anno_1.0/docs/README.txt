        Abstract Meaning Representation (AMR) Annotation Release 1.0
                       Linguistic Data Consortium

1.0 Overview

This release contains a sembank (semantic treebank) of over 13,000
English natural language sentences. Each sentence is paired with a
graph that represents its whole-sentence meaning in a tree-structure.

Meanings are encoded in Abstract Meaning Representation (AMR), a
language described in (Banarescu et al, 2013). AMR utilizes PropBank
frames, non-core semantic roles, within-sentence coreference, named
entity annotation, modality, negation, questions, quantities, and so
on to represent the semantic structure of a sentence largely
independent of its syntax.

More information about AMR, including annotation guidelines, can be
found at http://amr.isi.edu/language.html. Briefly:

  1) AMRs are rooted, labeled graphs. Like the Penn Treebank, AMRs
  are written in a text format that is readable by people and
  traversable by machines. As a simple example of the format, we
  represent "the boy wants to go" as:

    (w / want-01
      :ARG0 (b / boy)
      :ARG1 (g / go-02
              :ARG0 b))

  which can be paraphrased as: "There is a wanting event (w), whose
  wanter is a boy (b), and whose wanted-thing is a going event (g).
  The entity doing the going is the same boy (b)."

  2) AMR aims to abstract away from the syntactic structure of
  English, frequently assigning the same AMR to different sentences
  that mean the same thing:

    (a / adjust-01 
     :ARG0 (b / girl) 
     :ARG1 (m / machine)) 

     "The girl made adjustments to the machine."
     "The girl adjusted the machine."
     "The machine was adjusted by the girl."

  3) AMR incorporates entity recognition, co-reference, and semantic
  roles, but adds significant amounts of further information required
  to represent all of the contents of a sentence. This information
  includes modality, negation, questions, non-core semantic relations
  (e.g. purpose), event relations (e.g. causality), inverse relations,
  reification, etc.

  4) AMR makes extensive use of PropBank framesets (Kingsbury and
  Palmer, 2002; Palmer et al., 2005), applying them beyond verbs. For
  example, the phrase "bond investor" is represented with the frame
  "invest-01", even though the phrase contains no verbs:

    (i / invest-01
      :ARG0 (p / person)
      :ARG2 (b / bond))

  5) Single entities typically play multiple roles in an AMR. For
  example, the AMR for "Pascale was charged with public intoxication
  and resisting arrest" contains four instances of the variable "p":

    (c / charge-05
      :ARG1 (p / person
              :name (n / name :op1 "Pascale"))
      :ARG2 (a / and
              :op1 (i / intoxicate-01
                    :ARG1 p
                    :location (p2 / public))
              :op2 (r / resist-01
                     :ARG0 p
                     :ARG1 (a2 / arrest-01
                             :ARG1 p))))

  Such multiple role-playing may represent English pronouns,
  zero-pronouns, or control structures, but may also capture relations
  that are implicit in text.

  6) AMR is agnostic about how to derive meanings from strings, and
  vice-versa. In translating sentences to AMR, we do not dictate a
  particular sequence of rule applications, or provide alignments that
  reflect such rule sequences. This makes AMR annotation very fast,
  and it allows researchers to explore their own ideas about how
  strings are related to meanings.

  7) AMR is heavily biased towards English. It is not an Interlingua.


2.0 Contents

2.1 Data Profile

The following table summarizes the number of training, dev, and test
AMRs for each dataset in the release. Totals are also provided by
partition and dataset:

  Dataset           Training     Dev      Test      Totals
  ------------------------------------------------------------  
  BOLT DF MT            1061     133       133        1327    
  Weblog and WSJ           0     100       100         200
  BOLT DF English       1703     210       229        2142
  2009 Open MT           204       0         0         204
  Proxy reports         6603     826       823        8252
  Xinhua MT              741      99        86         926
  ------------------------------------------------------------
  Totals               10312    1368      1371       13051

2.2 File Inventory

  data/split

For those interested in a utilizing a standard/community partition for
AMR research (for instance in development of semantic parsers), this
directory contains 13051 AMRs split roughly 80/10/10 into
training/dev/test partitions, with most smaller datasets assigned to
one of the splits as a whole. Note that splits observe document
boundaries.

  data/split/dev

Directory containing 1368 dev-partitioned AMRs, across the following 5
dataset files. The number of AMRs in each text file is listed in
parentheses next to the file name:

  data/split/dev/amr-release-1.0-dev-bolt.txt (133)
  data/split/dev/amr-release-1.0-dev-consensus.txt (100)
  data/split/dev/amr-release-1.0-dev-dfa.txt (210)
  data/split/dev/amr-release-1.0-dev-proxy.txt (826)
  data/split/dev/amr-release-1.0-dev-xinhua.txt (99)

NOTE: These files are all UTF-8 Unicode English text, some with very
long lines.

  data/split/test

Directory containing 1371 test-partitioned AMRs, across the following 5
dataset files. The number of AMRs in each text file is listed in
parentheses next to the file name:

  data/split/test/amr-release-1.0-test-bolt.txt (133)
  data/split/test/amr-release-1.0-test-consensus.txt (100)
  data/split/test/amr-release-1.0-test-dfa.txt (229)
  data/split/test/amr-release-1.0-test-proxy.txt (823)
  data/split/test/amr-release-1.0-test-xinhua.txt (86)

  data/split/training

Directory containing 10312 training-partitioned AMRs, across the
following 5 dataset files. The number of AMRs in each text file is listed in
parentheses next to the file name:

  data/split/training/amr-release-1.0-training-bolt.txt (1061)
  data/split/training/amr-release-1.0-training-dfa.txt (1703)
  data/split/training/amr-release-1.0-training-mt09sdl.txt (204)
  data/split/training/amr-release-1.0-training-proxy.txt (6603)
  data/split/training/amr-release-1.0-training-xinhua.txt (741)

  data/unsplit

For those not interested in utilizing the training/dev/test AMR
partition, this directory contains the same 13051 AMRs unsplit
(i.e. with no train/dev/test partition), across the following 6
dataset files. The number of AMRs in each text file is listed in
parentheses next to the file name:

  data/unsplit/amr-release-1.0-bolt.txt (1327)
  data/unsplit/amr-release-1.0-consensus.txt (200)
  data/unsplit/amr-release-1.0-dfa.txt (2142)
  data/unsplit/amr-release-1.0-mt09sdl.txt (204)
  data/unsplit/amr-release-1.0-proxy.txt (8252)
  data/unsplit/amr-release-1.0-xinhua.txt (926)

NOTE: These files are all UTF-8 Unicode English text, some with very
long lines.

  docs/amr-guidelines-v1.1.pdf

The latest version of the guidelines under which the AMRs in this
release were produced.

  docs/README.txt

This file.

2.3 Structure and content of individual AMRs

Each AMR-sentence pair in the above files comprises the following data and
fields:

  - Header line containing a unique workset-sentence ID for the source
    string that has been AMR annotated (::id), a completion timestamp
    for the AMR (::date), an anonymized ID for the annotator who
    produced the AMR (::annotator), and a marker for the AMRs of
    dually-annotated sentences indicating whether the AMR is the
    preferred representation for the sentence (::preferred)

  - Header line containing the English source sentence that has been
    AMR annotated (::snt)

   - Header line indicating the date on which the AMR was last saved
    (::save-date), and the file name for the AMR-sentence pair
    (::file)

  - Graph containing the manually generated AMR tree for the source
    sentence (see the AMR guidelines for a full description of the
    structure and semantics of AMR graphs).

    NOTE: Proxy report AMRs have an additional field indicating the
    sentence content type (date, country, topic, summary, body, or
    body subordinate) (::snt-type)


3.0 Source data

The sentences that have been AMR annotated in this release are taken
from the following sources (their dataset shorthand appears in
parentheses).

3.1 BOLT Discussion forum MT data (bolt)

This discussion forum MT data was selected for AMR annotation because
it is rich in informal language, expressions of sentiment and opinion,
debates, power dynamics, and a broader spectrum of events
(e.g. communication events) all of which are not typically found in
traditional newswire data. It also illustrates how AMR is applied to
machine translation.

3.2 GALE Weblog and Wall Street Journal data (consensus)

This GALE weblog data in this dataset was selected for AMR annotation
because it contains informal language, as well as event phenomena of
interest to events researchers (e.g. causal relations, different
levels or granularities of events, irrealis events, fuzzy temporal
information, etc.)

The Wall Street Journal newswire data in this dataset was selected for
AMR annotation because these sentences contain an interesting
inventory of financial and economic events, and have been widely
annotated within the NLP community.

3.3 BOLT Discussion forum English source data (dfa)

This discussion forum data was selected from from LDC's BOLT -
Selected & Segmented Source Data for Annotation R4 corpus (LDC2012R77)
for AMR annotation because it is rich in informal language,
expressions of sentiment and opinion, debates, power dynamics, and a
broader spectrum of events (e.g. communication events) all of which
are not typically found in traditional newswire data.

3.4 Open MT Data (mt09sdl)

This data was selected from the NIST 2008-2012 Open Machine
Translation (OpenMT) Progress Test Sets corpus (LDC2013T07) for AMR
annotation because it is rich in events and event-relations commonly
found in newswire data, and illustrates how AMR is applied to machine
translations.

3.5 Narrative text "Proxy Reports" from newswire data (proxy)

This data was selected and segmented from the proxy report data in
LDC's DEFT Narrative Text Source Data R1 corpus (LDC2013E19) for AMR
annotation because they are developed from and thus rich in events and
event-relations commonly found in newswire data, but also have a
templatic, report-like structure which is more difficult for machines
to process.

Proxy reports were created from newswire articles selected from the 
English Gigaword Corpus, Fifth Edition. Articles were selected for 
topics of potential interest to DEFT project sponsors.

In proxy report creation, annotators are presented with a single 
newswire article and asked to fill in a proxy report header template 
with date, country, topic, and summary information. They also filled 
in the body of the report by editing and/or re-writing the content of 
the newswire article to approximate the style of an analyst report. 
All substantive information in the newswire document is retained in 
the proxy report.

The proxy report docid corresponds to the docid of the newswire that 
served as source material for the creation of the proxy report. For 
example, PROXY_AFP_ENG_20020529.0533.txt is the proxy report created 
from newswire document AFP_ENG_20020529.0533.xml.

3.6 Translated newswire data from Xinhua (xinhua)

This data was selected from LDC's English Chinese Translation Treebank
v 1.0 corpus (LDC2007T02) for AMR annotation because it is rich in
events and event-relations commonly found in newswire data, and
illustrates how AMR is applied to machine translation.


4.0 Annotation

Annotation for this AMR release was performed by over 25 annotators at
the University of Colorado, the Linguistic Data Consortium, and SDL.

4.1 Guidelines

The most-current version of the AMR guidelines can be found here:
<https://github.com/amrisi/amr-guidelines/blob/master/amr.md>

4.2 The AMR Editor

All AMR annotation is carried out through a web-based editing tool
that encourages speed and consistency. This tool was built by Ulf
Hermjakob at USC/ISI. The AMR Editor:

  1) Supports incremental AMR construction with rapid text-box
  commands.

  2) Highlights concepts that have PropBank framesets, displaying
  those framesets with example sentences.

  3) Pre-processes entities, dates, quantities, etc., making it easy
  for annotators to cut and paste semantic fragments into their AMRs.

  4) Provides annotation guidance, including lists of semantic
  relations (with examples), named entity types, and a search function
  that lets annotators query AMRs that were previously constructed by
  themselves or others. Search queries may be words, phrases, or AMR
  concepts.

  5) Has a built-in AMR Checker that flags typical errors, such as
  misspellings, omissions, illegal relations, etc.
 
  6) Includes administrative support tools for user-account creation,
  sharing of worksets, and annotator activity reports.

More details about the AMR Editor, including tutorial videos, can be
found at <http://amr.isi.edu/editor.html>


5.0 Acknowledgments

  From University of Colorado

We gratefully acknowledge the support of the National Science
Foundation Grant NSF: 0910992 IIS:RI: Large: Collaborative Research:
Richer Representations for Machine Translation and the support of
Darpa BOLT - HR0011-11-C-0145 and DEFT - FA-8750-13-2-0045 via a
subcontract from LDC. Any opinions, findings, and conclusions or
recommendations expressed in this material are those of the authors
and do not necessarily reflect the views of the National Science
Foundation, DARPA or the US government.

  From Information Sciences Institute (ISI)

Thanks to NSF (IIS-0908532) for funding the initial design of AMR, and
to DARPA MRP (FA-8750-09-C-0179) for supporting a group to construct
consensus annotations and the AMR Editor. The initial AMR bank was
built under DARPA DEFT FA-8750-13-2-0045 (PI: Stephanie Strassel;
co-PIs: Kevin Knight, Daniel Marcu, and Martha Palmer) and DARPA BOLT
HR0011-12-C-0014 (PI: Kevin Knight).

  From Linguistic Data Consortium (LDC)

This material is based on research sponsored by Air Force Research
Laboratory and Defense Advance Research Projects Agency under
agreement number FA8750-13-2-0045. The U.S. Government is authorized
to reproduce and distribute reprints for Governmental purposes
notwithstanding any copyright notation thereon. The views and
conclusions contained herein are those of the authors and should not
be interpreted as necessarily representing the official policies or
endorsements, either expressed or implied, of Air Force Research
Laboratory and Defense Advanced Research Projects Agency or the
U.S. Government.

We gratefully acknowledge the support of Defense Advanced Research
Projects Agency (DARPA) Machine Reading Program under Air Force
Research Laboratory (AFRL) prime contract no. FA8750-09-C-0184
Subcontract 4400165821. Any opinions, findings, and conclusion or
recommendations expressed in this material are those of the author(s)
and do not necessarily reflect the view of the DARPA, AFRL, or the US
government.

  From Language Weaver (SDL)

This work was partially sponsored by DARPA contract HR0011-11-C-0150
to LanguageWeaver Inc. Any opinions, findings, and conclusion or
recommendations expressed in this material are those of the author(s)
and do not necessarily reflect the view of the DARPA or the US
government.


6.0 Copyright Information

   Portions (c) 1987-1989 Dow Jones & Company, Inc., Portions (c) 2007
   Agence France Presse, Al-Ahram, Al Hayat, Al-Quds Al-Arabi, Asharq
   Al-Awsat, An Nahar, Assabah, China Military Online, Chinanews.com,
   Guangming Daily, Xinhua News Agency, Portions (c) 2002-2005,
   2007-2008 Agence France Presse, (c) 2002-2008 The Associated Press,
   (c) 2003-2004, 2007-2008 Central News Agency (Taiwan), (c) 1995,
   2003, 2007-2008 Los Angeles Times-Washington Post News Service,
   Inc., (c) 2002, 2004-2005, 2007-2008 New York Times, (c) 2001-2008
   Xinhua News Agency, Portions (c) 1994-1998 Xinhua News Agency

   (c) 2014 Trustees of the University of Pennsylvania


7.0 Authors

For further information on the contents of this corpus, please
contact the following contributors:

  Kevin Knight, ISI/USC                <knight@isi.edu>               
  --                                   --   
  Laura Baranescu, SDL                 <lbanarescu@sdl.com>
  Claire Bonial, Univ Colorado         <claire.bonial@colorado.edu>
  Madalina Georgescu, SDL              <mgeorgescu@sdl.com>
  Kira Griffitt, LDC                   <kiragrif@ldc.upenn.edu>
  Ulf Hermjakob, ISI/USC               <ulf@isi.edu>
  Daniel Marcu, SDL                    <dmarcu@sdl.com>
  Martha Palmer, Univ Colorado         <martha.palmer@colorado.edu>
  Nathan Schneider, LTI/CMU            <nschneid@cs.cmu.edu>

--------------------------------------------------------------------------
README created by Kira Griffitt on January 16, 2014
README updated by Kira Griffitt on January 27, 2014
README updated by Kira Griffitt on January 28, 2014
README updated by Kira Griffitt on January 30, 2014
README updated by Kira Griffitt on February 7, 2014
README updated by Kira Griffitt on February 11, 2014
README updated by Kira Griffitt on February 14, 2014
README updated by Kira Griffitt on March 14, 2014

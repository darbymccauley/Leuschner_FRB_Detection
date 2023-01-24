# LIMBO: Long Integration Mangetar Burst Observatory
## Project Overview:
LIMBO is an FRB observational project at the University of California, Berkeley. We make use of the Leuschner Student Observatory's 3.7m radio telescope to engage in long observations of galactic magnetars. Our pilot source is SGR1935+2154, which is most visible to us in the sky for extended periods of time (approximately 14hrs per day) and is known to repeat, making it an ideal observational candidate. This repository holds all developmental work. This project, done under the supervision of both Professors Wenbin Lu and Aaron Parsons of UC Berkeley.

- - - -

## Code:
The repository can be split into two main parts:

  1. src/fdmt: Contains the source code for the [FDMT dedispersion algorithm](https://ui.adsabs.harvard.edu/link_gateway/2017ApJ...835...11Z/arxiv:1411.5373) used during FRB observation.
  2. sims: Constains code for computer generated FRB simulations, `SimFRB`, as well as `WaveGen`, a package used to simulate FRBs in a lab using a Raspberry Pi and a PTS frequency synthesizer.

Darby McCauley 2022 darbymccauley@berkeley.edu

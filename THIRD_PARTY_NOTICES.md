# Sources and third party notices

The Apache-2.0 license covers this project's original code and documentation. Retained NASA source records, external research, and installed packages keep their own terms and attribution. We do not claim to relicense them.

## NASA data

NASA POWER data are provided by the NASA POWER Project at NASA Langley Research Center. This application uses monthly T2M and PRECTOTCORR from the public temporal point API. The records identify MERRA-2 as their meteorology source. Request URLs, dates, units, API versions and payload hashes travel with the frozen files and analysis exports. See the [monthly service](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/), [meteorology methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), and [POWER citation guidance](https://power.larc.nasa.gov/docs/acknowledgements/).

GISTEMP Team, 2026: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies. Data accessed 11 November 2026 at [GISTEMP](https://data.giss.nasa.gov/gistemp/). The retained land-only 250 km NetCDF and its exact hash are documented in [the comparison](evaluation/DATASET_CHECK.md).

Lenssen et al. (2024), *A GISTEMPv4 observational uncertainty ensemble*, Journal of Geophysical Research: Atmospheres, [doi:10.1029/2023JD040179](https://doi.org/10.1029/2023JD040179).

NASA names identify data sources. No NASA logo, endorsement, sponsorship or award is claimed. The project is separate from the established [KNMI Climate Explorer](https://climexp.knmi.nl/), which the challenge itself lists as an existing tool.

## Software

NumPy, SciPy and statsmodels provide numerical routines under their respective BSD licenses. They are installed from the package registry rather than copied into this repository. The full environment is pinned in requirements-lock.txt. Transitive packages include pandas, patsy, formulaic, interface_meta, narwhals, packaging, python-dateutil, typing_extensions, tzdata and wrapt. Their installed distributions retain their own license files and metadata.

- [NumPy license](https://github.com/numpy/numpy/blob/main/LICENSE.txt)
- [SciPy license](https://github.com/scipy/scipy/blob/main/LICENSE.txt)
- [statsmodels license](https://github.com/statsmodels/statsmodels/blob/main/LICENSE.txt)

The interface uses browser-native HTML, CSS, JavaScript and SVG with local system fonts. No external JavaScript library, stock photograph, third-party logo or downloaded font is bundled. GitHub Actions used by the build are pinned to source commits in the workflow.

## Research and requirements

[RESEARCH.md](RESEARCH.md), the evaluation protocols, and [verified competition requirements](submission/REQUIREMENTS.md) cite the relevant primary sources. We retain short excerpts and retrieval metadata for the event guides, rather than republishing their complete text. Those sources are not covered by our software license.


## Optional narrated-media production

Higgsfield Seedance 2.5 supplies the synthetic adult performance and native speech; its receipt and disclosure are in submission/higgsfield-generation.json. NASA input retains the data terms above. The instrumental bed and accents are synthesized by the project's own script. Local video authoring uses FFmpeg, Pillow and NumPy. Automatic timing uses faster-whisper, CTranslate2 and downloaded Whisper model weights; optional authoring versions are recorded separately in submission/requirements-media-lock.txt. These authoring packages are not added to application runtime dependencies. Their upstream licenses remain applicable.

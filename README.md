# Site map

### Description
Generating a site map by parsing all links from the specified

### Quickstart
##### Clone the repository and navigate to it:
```console
git clone git@github.com:quantumwaffy/site_map.git && cd $(basename $_ .git)
```
##### Run parser:
```console
make parse ARGS="-u your_URL [-d max_parsing_depth] [-c max_concurrent_requests_count]"
```

# HW03 Docker Image Size Report

| Repository           | Tag       | Size   |
|:---------------------|:----------|:-------|
| qbc12-airbnb-serving | optimized | 1.29GB |
| qbc12-airbnb-serving | naive     | 3.13GB |

## Analysis
<!-- TODO: Write 2-3 sentences explaining why the sizes differ and which you would use in production. -->
The naive image (3.13GB) uses the full `python:3.11` base image, which includes build tools, compilers, and OS packages never needed at runtime, and it installs dependencies in the same layer as the final image rather than discarding build-time artifacts. The optimized image (1.29GB) uses a multi-stage build: a `builder` stage installs packages with `pip install --prefix=/install`, and only the resulting installed files are copied into a slim `python:3.11-slim` final stage — discarding pip's cache, build dependencies, and compiler toolchains that the naive image keeps. In production, the optimized image is the clear choice: it pulls and starts faster and costs less to store and transfer at scale across multiple replicas.

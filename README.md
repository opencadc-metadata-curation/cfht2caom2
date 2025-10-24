# cfht2caom2
An application to generate CAOM2 Observations from CFHT FITS files for the instruments MegaPrime, WIRCam, SPIRou, SITELLE, and ESPaDOnS.

# How to Run CFHT

In an empty directory (the 'working directory'), on a machine with Docker installed:

1. In the master branch of this repository, find the scripts directory, and copy the file cfht_run.sh to the working directory. e.g.:

  ```
  wget https://raw.github.com/opencadc-metadata-curation/cfht2caom2/master/scripts/cfht_run.sh
  ```

2. Ensure the script is executable:

```
chmod +x cfht_run.sh
```

3. To run the application:

```
./cfht_run.sh
```

4. The `config.yml` file is configuration information for the ingestion. This file will be created in the executing directory the first time the script `cfht_run.sh` is run. It will work with the files names and described here. For a complete description of its content, see https://github.com/opencadc/collection2caom2/wiki/config.yml.

5. The ways to tell this tool the work to be done:

    1. provide a file containing the list of file names to process, one per line, and the `config.yml` file containing the entries `use_local_files` set to `False`. The 'todo' file is provided  as a file named `todo.txt` in the working directory, as specified in `config.yml`.
    2. provide the files to be processed in a list of `data_sources` directories (may be a list of length 1), and the `config.yml` file containing the entries `use_local_files` set to `True`
    
    If the `store` task type is present, the files will be transferred to CADC, and stored in the `CFHT` archive. If `use_local_files` is set to `True`, and `store_newer_files_only` is also set to `True`, only newer files will be transferred to CADC.

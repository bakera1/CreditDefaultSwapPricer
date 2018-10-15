rem needed to play nicely with artifactory
rem avoid No enum constant org.jfrog.repomd.pypi.model.PypiMetadata.MetadataVersion.v2_1
rem pip install wheel==0.30.0
rem pip install twine
rem pip install setuptools==36.0.0
twine upload --repository artifactory dist/* --verbose

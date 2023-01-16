Modifications to deletion timing scripts from Jaoa Lopes at CERN (original at 
https://gitlab.cern.ch/fts/scripts/-/tree/master/deletion-test )
Script records upload and deletion times
Script prints slowest deletion time
deletion_test.py --source file:///scratch/ijj87/Data/file-4GB --dest davs://webdav.echo.stfc.ac.uk:1094/dteam:test/ian_johnson/file-4GB- \
--workers 10 --files 10 -o upload-webdav.echo-nfiles-10-nworkers-10-pass-01 

Here, the file URL after --source is a data file to upload. URL after --dest serves as the stem for a series of upload targets, taking a sequential index 0..N

The deletion step is
deletion_test.py --dest davs://webdav.echo.stfc.ac.uk:1094/dteam:test/ian_johnson/file-4GB- \
--workers 10 --files 10 -o upload-webdav.echo-nfiles-10-nworkers-10-pass-01

Typical output:
Delete TOTAL TIME 14.769433\
AVERAGE TIME TO DELETE = 3.692429\
LONGEST TIME TO DELETE = 14.734606
MEDIAN OF TIME TO DELETE = 1.136115

This will create two pickle files upload-webdav.echo-nfiles-10-nworkers-10-pass-01{results,stats}.pkl containing respectively the deletion times for each target file, 
and overall stats (mean, median, max) for the group of deletions


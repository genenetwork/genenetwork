import sys

import utilities
import datastructure
import genotypes
import probesets
# import calculate

"""
For:    Ash
Date:   2014-02-07
Function:
    For BXD group, get a probesetfreeze name list.
"""
def probesetfreeze_list(outputdir):
    #
    inbredsetid = 1
    #
    probesetfreezes = datastructure.get_probesetfreezes(inbredsetid)
    print "From DB, get %d probesetfreezes" % (len(probesetfreezes))
    file = open(outputdir + '/' + 'probesetfreezes.txt', 'w+')
    #
    for probesetfreeze in probesetfreezes:
        #
        print probesetfreeze
        probesetfreezeid = probesetfreeze[0]
        probesetfreezename = probesetfreeze[1]
        probesetfreezefullname = probesetfreeze[2]
        #
        file.write("%s\t" % probesetfreezeid)
        file.write("%s" % probesetfreezefullname)
        file.write("\n")
        file.flush()
        #
    file.close()
        
"""
For:    Ash
Date:   2014-02-05
Function:
    For BXD group, calculate correlations with genotypes and probesets.
"""
def bxd_correlations():
    #
    inbredsetid = 1
    genofile = "/home/leiyan/gn/web/genotypes/BXD.geno"
    outputdir = "/home/leiyan/gn2/wqflask/maintenance/dataset/datadir/20140205_Ash_correlations/output"
    #
    t = genotypes.load_genos(genofile)
    genostrains = t[0]
    genos = t[1]
    print "From geno file, get %d strains" % (len(genostrains))
    print "From geno file, get %d genos" % (len(genos))
    #
    probesetfreezes = datastructure.get_probesetfreezes(inbredsetid)
    print "From DB, get %d probesetfreezes" % (len(probesetfreezes))
    for probesetfreeze in probesetfreezes:
        correlations(outputdir=outputdir, genos=genos, probesetfreeze=probesetfreeze)
    
def correlations(outputdir, genos, probesetfreeze):
    print probesetfreeze
    probesetfreezeid = probesetfreeze[0]
    probesetfreezename = probesetfreeze[1]
    probesetfreezefullname = probesetfreeze[2]
    #
    outputfile = open("%s/%d_%s.txt" % (outputdir, probesetfreezeid, probesetfreezename), "w+")
    outputfile.write("%s\t" % "ProbeSet Id")
    outputfile.write("%s\t" % "ProbeSet Name")
    outputfile.write("%s\t" % "Geno Name")
    outputfile.write("%s\t" % "Overlap Number")
    outputfile.write("%s\t" % "Pearson r")
    outputfile.write("%s\t" % "Pearson p")
    outputfile.write("%s\t" % "Spearman r")
    outputfile.write("%s\t" % "Spearman p")
    outputfile.write("\n")
    outputfile.flush()
    #
    probesetxrefs = probesets.get_probesetxref(probesetfreezeid)
    print "Get %d probesetxrefs" % (len(probesetxrefs))
    #
    for probesetxref in probesetxrefs:
        #
        probesetid = probesetxref[0]
        probesetdataid = probesetxref[1]
        probeset = probesets.get_probeset(probesetid)
        probesetname = probeset[1]
        probesetdata = probesets.get_probesetdata(probesetdataid)
        probesetdata = zip(*probesetdata)
        probesetdata = utilities.to_dic([strain.lower() for strain in probesetdata[1]], probesetdata[2])
        #
        for geno in genos:
            genoname = geno['locus']
            outputfile.write("%s\t" % probesetid)
            outputfile.write("%s\t" % probesetname)
            outputfile.write("%s\t" % genoname)
            #
            dic1 = geno['dicvalues']
            dic2 = probesetdata
            keys, values1, values2 = utilities.overlap(dic1, dic2)
            rs = calculate.correlation(values1, values2)
            #
            outputfile.write("%s\t" % len(keys))
            outputfile.write("%s\t" % rs[0][0])
            outputfile.write("%s\t" % rs[0][1])
            outputfile.write("%s\t" % rs[1][0])
            outputfile.write("%s\t" % rs[1][1])
            outputfile.write("\n")
            outputfile.flush()
    #
    outputfile.close()
    
"""
For:    Ash
Date:   2014-02-10
Function:
    For BXD group, calculate correlations with genotypes and probesets.
    given probesetfreezes
"""
def bxd_correlations_givenprobesetfreezes(probesetfreezesfile, outputdir):
    #
    inbredsetid = 1
    genofile = "/home/leiyan/gn/web/genotypes/BXD.geno"
    #
    t = genotypes.load_genos(genofile)
    genostrains = t[0]
    genos = t[1]
    print "From geno file, get %d strains" % (len(genostrains))
    print "From geno file, get %d genos" % (len(genos))
    #
    file = open(probesetfreezesfile, 'r')
    for line in file:
        line = line.strip()
        cells = line.split()
        probesetfreezeid = cells[0]
        probesetfreeze = datastructure.get_probesetfreeze(probesetfreezeid)
        correlations(outputdir=outputdir, genos=genos, probesetfreeze=probesetfreeze)
    file.close()

"""
Date:   2014-04-01
Function:
    show how many probeset records
    given probesetfreezes
"""
def bxd_givenprobesetfreezes(probesetfreezesfile):
    file = open(probesetfreezesfile, 'r')
    for line in file:
        line = line.strip()
        cells = line.split()
        probesetfreezeid = cells[0]
        probesetfreeze = datastructure.get_probesetfreeze(probesetfreezeid)
        probesetfreezename = probesetfreeze[1]
        probesetfreezefullname = probesetfreeze[2]
        probesetxrefs = probesets.get_probesetxref(probesetfreezeid)
        print "%s\t%s\t%s\t%d" % (probesetfreezeid, probesetfreezename, probesetfreezefullname, len(probesetxrefs))
    file.close()

if __name__ == "__main__":
    print("command line arguments:\n\t%s" % sys.argv)
    # bxd_correlations_givenprobesetfreezes(sys.argv[1], sys.argv[2])
    probesetfreeze_list(sys.argv[1])
    print("exit successfully")

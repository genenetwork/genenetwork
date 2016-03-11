import sys
import utilities

def get_publishxrefs(inbredsetid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT PublishXRef.`Id`, PublishXRef.`PhenotypeId`, PublishXRef.`PublicationId`, PublishXRef.`DataId`
        FROM PublishXRef
        WHERE PublishXRef.`InbredSetId`=%s
        """
    cursor.execute(sql, (inbredsetid))
    return cursor.fetchall()
    
def get_phenotype(phenotypeid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT Phenotype.`Original_description`, Phenotype.`Pre_publication_description`, Phenotype.`Post_publication_description`
        FROM Phenotype
        WHERE Phenotype.`Id`=%s
        """
    cursor.execute(sql, (phenotypeid))
    return cursor.fetchone()
    
def get_publication(publicationid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT Publication.`Authors`, Publication.`Abstract`
        FROM Publication
        WHERE Publication.`Id`=%s
        """
    cursor.execute(sql, (publicationid))
    return cursor.fetchone()
    
def get_publishdata(publishdataid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT Strain.`Id`, Strain.`Name`, PublishData.`value`
        FROM PublishData, Strain
        WHERE PublishData.`Id`=%s
        AND PublishData.`StrainId`=Strain.`Id`
        """
    cursor.execute(sql, (publishdataid))
    return cursor.fetchall()

def get_publishdatan(publishdataid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT Strain.`Id`, Strain.`Name`, NStrain.`count`
        FROM NStrain, Strain
        WHERE NStrain.`DataId`=%s
        AND NStrain.`StrainId`=Strain.`Id`
        """
    cursor.execute(sql, (publishdataid))
    return cursor.fetchall()

def get_publishdatase(publishdataid):
    cursor, con = utilities.get_cursor()
    sql = """
        SELECT Strain.`Id`, Strain.`Name`, PublishSE.`error`
        FROM PublishSE, Strain
        WHERE PublishSE.`DataId`=%s
        AND PublishSE.`StrainId`=Strain.`Id`
        """
    cursor.execute(sql, (publishdataid))
    return cursor.fetchall()

def fetch(inbredsetid, filename):
    # parameters
    phenotypesfile = open(filename, 'w+')
    #
    phenotypesfile.write("id\tAuthors\tOriginal_description\tPre_publication_description\tPost_publication_description\t")
    # open db
    cursor, con = utilities.get_cursor()
    # get strain list
    strains = []
    sql = """
        SELECT Strain.`Name`
        FROM StrainXRef, Strain
        WHERE StrainXRef.`StrainId`=Strain.`Id`
        AND StrainXRef.`InbredSetId`=%s
        ORDER BY StrainXRef.`OrderId`
        """
    cursor.execute(sql, (inbredsetid))
    results = cursor.fetchall()
    for row in results:
        strain = row[0]
        strain = strain.lower()
        strains.append(strain)
    print "get %d strains: %s" % (len(strains), strains)
    phenotypesfile.write('\t'.join([strain.upper() for strain in strains]))
    phenotypesfile.write('\n')
    phenotypesfile.flush()
    # phenotypes
    sql = """
        SELECT PublishXRef.`Id`, Publication.`Authors`, Phenotype.`Original_description`, Phenotype.`Pre_publication_description`, Phenotype.`Post_publication_description`
        FROM (PublishXRef, Phenotype, Publication)
        WHERE PublishXRef.`InbredSetId`=%s
        AND PublishXRef.`PhenotypeId`=Phenotype.`Id`
        AND PublishXRef.`PublicationId`=Publication.`Id`
        """
    cursor.execute(sql, (inbredsetid))
    results = cursor.fetchall()
    print "get %d phenotypes" % (len(results))
    for phenotyperow in results:
        publishxrefid = phenotyperow[0]
        authors = utilities.clearspaces(phenotyperow[1])
        original_description = utilities.clearspaces(phenotyperow[2])
        pre_publication_description = utilities.clearspaces(phenotyperow[3])
        post_publication_description = utilities.clearspaces(phenotyperow[4])
        phenotypesfile.write("%s\t%s\t%s\t%s\t%s\t" % (publishxrefid, authors, original_description, pre_publication_description, post_publication_description))
        sql = """
            SELECT Strain.Name, PublishData.value
            FROM (PublishXRef, PublishData, Strain)
            WHERE PublishXRef.`InbredSetId`=%s
            AND PublishXRef.Id=%s
            AND PublishXRef.DataId=PublishData.Id
            AND PublishData.StrainId=Strain.Id
        """
        cursor.execute(sql, (inbredsetid, publishxrefid))
        results = cursor.fetchall()
        print "get %d values" % (len(results))
        strainvaluedic = {}
        for strainvalue in results:
            strainname = strainvalue[0]
            strainname = strainname.lower()
            value = strainvalue[1]
            strainvaluedic[strainname] = value
        for strain in strains:
            if strain in strainvaluedic:
                phenotypesfile.write(str(strainvaluedic[strain]))
            else:
                phenotypesfile.write('x')
            phenotypesfile.write('\t')
        phenotypesfile.write('\n')
        phenotypesfile.flush()
    # release
    phenotypesfile.close()

def delete_phenotype_publishxrefid(publishxrefid, inbredsetid):
    cursor, con = utilities.get_cursor()
    sql = """
        DELETE Phenotype
        FROM PublishXRef,Phenotype
        WHERE PublishXRef.`Id`=%s
        AND PublishXRef.`InbredSetId`=%s
        AND PublishXRef.`PhenotypeId`=Phenotype.`Id`
        """
    cursor.execute(sql, (publishxrefid, inbredsetid))
    rowcount = cursor.rowcount
    con.close()
    return rowcount

def delete_publishdata_publishxrefid(publishxrefid, inbredsetid):
    cursor, con = utilities.get_cursor()
    sql = """
        DELETE PublishData
        FROM PublishXRef,PublishData
        WHERE PublishXRef.`Id`=%s
        AND PublishXRef.`InbredSetId`=%s
        AND PublishXRef.`DataId`=PublishData.`Id`
        """
    cursor.execute(sql, (publishxrefid, inbredsetid))
    sql = """
        DELETE PublishSE
        FROM PublishXRef,PublishSE
        WHERE PublishXRef.`Id`=%s
        AND PublishXRef.`InbredSetId`=%s
        AND PublishXRef.`DataId`=PublishSE.`DataId`
        """
    cursor.execute(sql, (publishxrefid, inbredsetid))
    sql = """
        DELETE NStrain
        FROM PublishXRef,NStrain
        WHERE PublishXRef.`Id`=%s
        AND PublishXRef.`InbredSetId`=%s
        AND PublishXRef.`DataId`=NStrain.`DataId`
        """
    cursor.execute(sql, (publishxrefid, inbredsetid))
    con.close()

def delete_publishxref(publishxrefid, inbredsetid):
    cursor, con = utilities.get_cursor()
    sql = """
        DELETE PublishXRef
        FROM PublishXRef
        WHERE PublishXRef.`Id`=%s
        AND PublishXRef.`InbredSetId`=%s
        """
    cursor.execute(sql, (publishxrefid, inbredsetid))
    rowcount = cursor.rowcount
    con.close()
    return rowcount

def delete(publishxrefid, inbredsetid):
    delete_publishdata_publishxrefid(publishxrefid, inbredsetid)
    delete_phenotype_publishxrefid(publishxrefid, inbredsetid)
    return delete_publishxref(publishxrefid, inbredsetid)

if __name__ == "__main__":
    print("command line arguments:\n\t%s" % sys.argv)
    fetch(inbredsetid=51, filename='hcp.pheno')
    print("exit successfully")

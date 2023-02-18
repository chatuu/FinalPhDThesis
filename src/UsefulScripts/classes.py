from headers import *
from functions import *


scale = 1.3562/1.9291582726279203

class CutTableEntries:
    """Get saved entries in histogram file and return as a python list

    Returns:
        list: list of entries without pot scaling
    """

    def __init__(self, inputFile):
        """Initialize input variables

        Args:
            inputFile (string): Input file name and location

        Returns:
            list: Python list
        """
        f = ROOT.TFile.Open(inputFile)

        muonIDHist = f.Get("npngsMuonID") 
        pionIDHist = f.Get("npngsPionID") 
        hitIDHist  = f.Get("npngsHitID") 
        kIDHist    = f.Get("npngsKID")

        muonIDHist.SetDirectory(0)
        pionIDHist.SetDirectory(0)
        hitIDHist .SetDirectory(0)
        kIDHist   .SetDirectory(0)

        muonIDEvents = GetAllEvents(muonIDHist)
        pionIDEvents = GetAllEvents(pionIDHist)
        hitIDEvents  = GetAllEvents(hitIDHist)
        kIDEvents    = GetAllEvents(kIDHist)

        f.Close()

        self.events = [muonIDEvents,pionIDEvents,hitIDEvents,kIDEvents]

    def GetEvents(self):
        return self.events



class LoadFile:    
    """This class is made to load ROOT file and to do following:    \n
        1.  Print Contents on terminal as a table: \n
        :param  fileName:   Name of the ROOT File that ends with .root
        :type   fileName:   .root
    """
    def __init__(self, fileName):
        self.file   =   ROOT.TFile.Open(fileName,"READ")
        self.Trees  =   []
        self.TH1    =   [] 
        self.TH2    =   []
        self.pot    =   []

        keys = self.file.GetListOfKeys()
        i = 0
        j = 0
        for key in keys:
            #print(key.GetClassName())
            if(key.GetClassName() == "TTree"):
                self.Trees.append(self.file.Get(key.GetName()))

            if ((key.GetClassName() == 'TH1D') and (key.GetName()=='TotalPOT')):
                self.potHist = self.file.Get(key.GetName())
                self.potHist.SetDirectory(0)

            if(key.GetClassName() == "TDirectoryFile"):
                dir = self.file.Get(key.GetName())
                dir.cd()
                hist = dir.Get('hist')
                pot  = dir.Get('pot')
                hist.SetDirectory(0)
                pot.SetDirectory(0)
                self.pot.append(pot)
                hist.SetName(key.GetName())
                self.TH1.append(hist)

    def PrintContent(self):
        #scale = 1.42283/5.5167
        """This function prints the file contents as a table in terminal: \n
            +------------+-------------------+-------------+-------------------+-------------------+
            | Number     | Object Class Name | Object Name | Number of Entries |        POT        |
            +============+===================+=============+===================+===================+
            |            |       TTree       |             |                   |                   |
            +------------+-------------------+-------------+-------------------+-------------------+
            |            |       TH2         |             |                   |                   |
            +------------+-------------------+-------------+-------------------+-------------------+
            |            |       TH1         |             |                   |                   |
            +------------+-------------------+-------------+-------------------+-------------------+

        .. note:: **Usage:** ``loadFileObject.PrintContent()``
        """
        table_data = []
        table_data.append(['Number', 'Object Class Name', 'Object Name', 'Number of Entries', 'pot', 'Under bin', 'Over Bin'])
        i = 0
        for tree in self.Trees:
            #treeInfo    =   tree.GetTreeInfo()
            table_data.append([i, "TTree", tree.GetName(),tree.GetEntries(), "N/A", "N/A", "N/A"])
            i += 1
        for hist, pot in zip(self.TH1, self.pot):
            #treeInfo    =   tree.GetTreeInfo()
            nBins = hist.GetNbinsX()
            table_data.append([i, hist.ClassName(), hist.GetName(),int(hist.Integral(1,-1)), pot.GetBinContent(1), hist.GetBinContent(0), hist.GetBinContent(nBins + 1)])
            i += 1

        table = AsciiTable(table_data)
        print(table.table)

    def SaveCSV(self, filename):
        """Save file content as a csv file

        Args:
            filename (string): name of output csv file
        """
        with open(filename, "w", newline='') as csvfile:
            fieldnames = [  'Number'           , 
                            'Object Class Name', 
                            'Object Name'      , 
                            'Number of Entries', 
                            'pot'              , 
                            'Under bin'        , 
                            'Over Bin']
            
            writer     = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            i           = 0

            for tree in self.Trees:
                writer.writerow({
                                    'Number'            : i                 ,
                                    'Object Class Name' : "TTree"           ,  
                                    'Object Name'       : tree.GetName()    ,
                                    'Number of Entries' : tree.GetEntries() ,
                                    'pot'               : "N/A"             ,
                                    'Under bin'         : "N/A"             ,
                                    'Over Bin'          : "N/A"
                                })
                i += 1

            for hist, pot in zip(self.TH1, self.pot):
                nBins = hist.GetNbinsX()
                writer.writerow({
                                    'Number'            : i                              ,
                                    'Object Class Name' : hist.ClassName()               ,  
                                    'Object Name'       : hist.GetName()                 ,
                                    'Number of Entries' : round(hist.Integral(1, -1), 2) ,
                                    'pot'               : pot.GetBinContent(1)           ,
                                    'Under bin'         : hist.GetBinContent(0)          ,
                                    'Over Bin'          : hist.GetBinContent(nBins + 1)
                                })
                i += 1

    def GetTrees(self, numbers):
        """This function returns the requested ROOT Trees.

        :param numbers: A list that contains Tree indeces according to the table printed.
        :type numbers: A python list
        :return: A list that contains requested Trees
        :rtype: A python list
        .. note:: **Usage:** ``loadFileObject.GetTrees([0, 1, 2 ,3...])``
        """
        treeList = []
        for num in numbers:
            treeList.append(self.Trees[num])
        return treeList

    def GetHists(self, numbers):
        """This function returns the requested ROOT Trees.

        :param numbers: A list that contains Tree indeces according to the table printed.
        :type numbers: A python list
        :return: A list that contains requested Trees
        :rtype: A python list
        .. note:: **Usage:** ``loadFileObject.GetTrees([0, 1, 2 ,3...])``
        """
        histList = []
        for num in numbers:
            histList.append(self.TH1[num])
        return histList

    def GetPOTHist(self):
        return self.potHist



    def Close(self):
        """This function is made to close file opened when constructing LoadFile. \n
        .. note:: **Usage:** ``loadFileObject.CloseFile()``
        .. code-block:: python

            # Inside top-level docs/ directory. make html
        """
        self.file.Close()

class CutTableCell:
    """ This class calculate number of events by iterating through TTree 
        for a given ROOT file and number of events will be saved to TH1
    """
    def __init__(self, inputFile, outFile, inttype, iscc):
        """Initialize class with input parameters

        Args:
            inputFile (string): Input file name and location
            outFile (string): Output file name and location
            inttype (int): Interaction type
            iscc (int): Is Charged-Current? yes = 1 no = 0
        """
        
        self.inFile  = inputFile
        self.outFile = outFile

        f = LoadFile(inputFile)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        npngsMuonID = ROOT.TH1D("npngsMuonID", "", 10, 0, 10)
        npngsMuonID.SetDirectory(0)

        npngsPionID = ROOT.TH1D("npngsPionID", "", 10, 0, 10)
        npngsPionID.SetDirectory(0)

        npngsHitID = ROOT.TH1D("npngsHitID", "", 10, 0, 10)
        npngsHitID.SetDirectory(0)
        
        npngsKID = ROOT.TH1D("npngsKID", "", 10, 0, 10)
        npngsKID.SetDirectory(0)


        for event in tree:
            muonID       = getattr(event, "BestKalmanMuonID" ) 
            pionID       = getattr(event, "FinalPionID"      )
            recoT        = getattr(event, "RecoTKalman"      )
            kID          = getattr(event, "NewKinematicScore")
            hitID        = getattr(event, "FinalHitScore"    )
            weight       = getattr(event, "weight"           )
            npngs        = getattr(event, "nProngs"          )
            eventinttype = getattr(event, "IntType"          )
            eventisCC    = getattr(event, "IsCC"             )

            if (int(inttype) == 999):
                if (muonID > 0.4):
                    npngsMuonID.Fill(npngs, weight)
                    
                    if (pionID > 0.3):
                        npngsPionID.Fill(npngs, weight)

                        if (hitID > 0.46):
                            npngsHitID.Fill(npngs, weight)

                            if ((recoT >= 0) and (kID > 0.84)):
                                npngsKID.Fill(npngs, weight)
            else:
                if ((eventinttype == int(inttype)) and (eventisCC == int(iscc))):
                    if (muonID > 0.4):
                        npngsMuonID.Fill(npngs, weight)
                        
                        if (pionID > 0.3):
                            npngsPionID.Fill(npngs, weight)

                            if (hitID > 0.46):
                                npngsHitID.Fill(npngs, weight)

                                if ((recoT >= 0) and (kID > 0.84)):
                                    npngsKID.Fill(npngs, weight)
                
                elif (int(iscc) == 0 and (eventisCC == 0)):
                     if (muonID > 0.4):
                        npngsMuonID.Fill(npngs, weight)
                        
                        if (pionID > 0.3):
                            npngsPionID.Fill(npngs, weight)

                            if (hitID > 0.46):
                                npngsHitID.Fill(npngs, weight)

                                if ((recoT >= 0) and (kID > 0.84)):
                                    npngsKID.Fill(npngs, weight)


        fOut = ROOT.TFile(outFile, "RECREATE")
        fOut.cd()
        npngsMuonID.Write()
        npngsPionID.Write()
        npngsHitID.Write()
        npngsKID.Write()
        fOut.Write()
        fOut.Close()

        f.Close()
        print(f"{outFile} created successfully.!")






class CreateBkgdTFile:
    """Create reconstructed |t| plot and save it to a ROOT files

    Returns:
        TFile: TFile That contains TH1
    """
    
    def __init__(self, inFile, outFile):
        """Constructor for CreateRecoTFile

        Args:
            inFile (string): input file name
            outFileName (string): output file name
        """
        self.inFile  = inFile
        self.outFile = outFile

        f = LoadFile(inFile)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        hist = ROOT.TH1D("hist","", 200, 0, 1)
        hist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            weight      = getattr(event, "weight"           )
            #shift       = getattr(event, "_")

            ############################################################
            # Background Control Region Cuts                           #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                ((pionID      <  0.05)  or 
                 (hitID       <  0.05)) and 
                (kinematicID  >  0.84 ) and 
                (recoT        >= 0    )):
                hist.Fill(recoT, weight)

            else:
                continue

        hist.Scale(scale)
        newHist = CalculateStatisticalErrorBinByBin(hist)        
        newHist.SetDirectory(0)
        newHist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(outFile, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()
        print(f"Successfully created {outFile} CreateBkgdTFile")

class CreateSigTFile:
    """Create reconstructed |t| plot and save it to a ROOT files

    Returns:
        TFile: TFile That contains TH1
    """
    
    def __init__(self, inFile, outFile):
        """Constructor for CreateRecoTFile

        Args:
            inFile (string): input file name
            outFileName (string): output file name
        """
        self.inFile  = inFile
        self.outFile = outFile

        f = LoadFile(inFile)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        hist = ROOT.TH1D("hist","", 200, 0, 1)
        hist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            weight      = getattr(event, "weight"           )
            #shift       = getattr(event, "_")

            ############################################################
            # Signal Region Cuts                                       #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                (pionID       >  0.3  ) and 
                (hitID        >  0.46 ) and 
                (kinematicID  >  0.84 ) and 
                (recoT        >= 0    )):
                hist.Fill(recoT, weight)

            else:
                continue

        hist.Scale(scale)                
        newHist = CalculateStatisticalErrorBinByBin(hist)        
        newHist.SetDirectory(0)
        newHist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(outFile, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()
        print(f"Successfully created {outFile} CreateSigTFile")

class CreateSigTFileAfterMuonIDCut:
    """Create reconstructed |t| plot and save it to a ROOT files

    Returns:
        TFile: TFile That contains TH1
    """
    
    def __init__(self, inFile, outFile):
        """Constructor for CreateRecoTFile

        Args:
            inFile (string): input file name
            outFileName (string): output file name
        """
        self.inFile  = inFile
        self.outFile = outFile

        f = LoadFile(inFile)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        hist = ROOT.TH1D("hist","", 200, 0, 1)
        hist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            weight      = getattr(event, "weight"           )
            #shift       = getattr(event, "_")

            ############################################################
            # Background Control Region Cuts                           #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                (recoT        >= 0    )):
                hist.Fill(recoT, weight)

            else:
                continue
    
        newHist = CalculateStatisticalErrorBinByBin(hist)        
        newHist.SetDirectory(0)
        newHist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(outFile, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()
        print(f"Successfully created {outFile}")



class CreateBkgdDataTFile:
    """Create reconstructed |t| plot and save it to a ROOT files

    Returns:
        TFile: TFile That contains TH1
    """
    
    def __init__(self, inFile, outFile):
        """Constructor for CreateRecoTFile

        Args:
            inFile (string): input file name
            outFileName (string): output file name
        """
        self.inFile  = inFile
        self.outFile = outFile

        f = LoadFile(inFile)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        hist = ROOT.TH1D("hist","", 200, 0, 1)
        hist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            #weight      = getattr(event, "weight"           )
            #shift       = getattr(event, "_")

            ############################################################
            # Background Control Region Cuts                           #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                ((pionID      <  0.05)  or 
                 (hitID       <  0.05)) and 
                (kinematicID  >  0.84 ) and 
                (recoT        >= 0    )):
                hist.Fill(recoT)

            else:
                continue
    
        newHist = CalculateStatisticalErrorBinByBin(hist)        
        newHist.SetDirectory(0)
        newHist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(outFile, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()
        print(f"Successfully created {outFile} CreateBkgdDataTFile")
            


class CreateTRatio:
    """Create |t| ratio plot with error bars

    Returns:
        TH1D: |t| ratio histogram
    """
    def __init__(self, fileName, outFname):
        """Constructor for |t| ratio plot

        Args:
            fileName (string): file name of TTree
            outFname (string): output file name to save TH1
        """
        self.fileName = fileName
        self.outFName = outFname

    def CalculateRatio(self):
        f = LoadFile(self.fileName)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        sigHist = ROOT.TH1D("bkgdHistInSigRegion", "", 200, 0, 1)
        sigHist.SetDirectory(0)

        backHist = ROOT.TH1D("bkgdHistInBackRegion", "", 200, 0, 1)
        backHist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            weight      = getattr(event, "weight"           )
            #shift       = getattr(event, "_")

            ############################################################
            # Signal Region Cuts                                       #
            ############################################################
            if ((muonID      >= 0.4) and 
                (pionID      >  0.3) and 
                (hitID       > 0.46) and 
                (kinematicID > 0.84) and 
                (recoT       >=0   )):
                sigHist.Fill(recoT, weight)

            ############################################################
            # Background Control Region Cuts                           #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                ((pionID      <  0.05)  or 
                 (hitID       <  0.05)) and 
                (kinematicID  >  0.84 ) and
                (recoT        >= 0    )):
                backHist.Fill(recoT, weight)
                
        hist = CalculateErrorOfRatioHist(backHist, sigHist)
        #hist = CalculateErrorOfRatioHist(backHist, sigHist)
        hist.SetDirectory(0)
        hist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(self.outFName, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()

class CreateTRatioGENIEKnobs:
    """Create |t| ratio plot with error bars by applying GENIE Shifts

    Returns:
        TH1D: |t| ratio histogram
    """
    def __init__(self, fileName, outFname):
        """Constructor for |t| ratio plot

        Args:
            fileName (string): file name of TTree
            outFname (string): output file name to save TH1
        """
        self.fileName = fileName
        self.outFName = outFname

    def CalculateRatio(self):
        f = LoadFile(self.fileName)
        f.PrintContent()
        tree = f.GetTrees([0])[0]

        sigHist = ROOT.TH1D("bkgdHistInSigRegion", "", 200, 0, 1)
        sigHist.SetDirectory(0)

        backHist = ROOT.TH1D("bkgdHistInBackRegion", "", 200, 0, 1)
        backHist.SetDirectory(0)

        for event in tree:
            muonID      = getattr(event, "BestKalmanMuonID" )
            pionID      = getattr(event, "FinalPionID"      )       
            hitID       = getattr(event, "FinalHitScore"    )       
            kinematicID = getattr(event, "NewKinematicScore")           
            recoT       = getattr(event, "RecoTKalman"      )   
            weight      = getattr(event, "weight"           )
            shift       = getattr(event, "_systshift_weight")

            ############################################################
            # Signal Region Cuts                                       #
            ############################################################
            if ((muonID      >= 0.4) and 
                (pionID      >  0.3) and 
                (hitID       > 0.46) and 
                (kinematicID > 0.84) and 
                (recoT       >=0   )):
                sigHist.Fill(recoT, (weight*shift))

            ############################################################
            # Background Control Region Cuts                           #
            ############################################################
            if ((muonID       >= 0.4  ) and 
                ((pionID      <  0.05)  or 
                 (hitID       <  0.05)) and 
                (kinematicID  >  0.84 ) and 
                (recoT        >= 0    )):
                backHist.Fill(recoT, (weight*shift))
                
        hist = CalculateErrorOfRatioHist(backHist, sigHist)
        #hist = CalculateErrorOfRatioHist(backHist, sigHist)
        hist.SetDirectory(0)
        hist.SetName(f"hist_{randint(1000, 9999)}")
        
        fout = ROOT.TFile(self.outFName, "RECREATE")
        fout.cd()
        hist.Write()
        fout.Write()
        fout.Close()
        f.Close()


        

class CompleteCutTable:
    """Creates the complete Cut Table
    """

    def __init__(self, csvName, title, rows):
        """Constructor for Complete Cut Table

        Args:
            csvName (string): Name of the csv file
            title (string): Title of the Table
            rows (list): list of CutTable rows
        """
        self.rows    = rows
        self.csvName = csvName
        self.title   = title

    def PrintCutTable(self):
        """Create ASCII Table and print to Terminal
        """
        """Prints cut table to the Terminal
        """
        table_data = []
        table_data.append(['Cut Name'    , 
                            'CC COH'     , 
                            'CC QE'      , 
                            'CC RES'     , 
                            'CC DIS'     , 
                            'CC MEC'     , 
                            'NC'         , 
                            'Other'      , 
                            'Total Bkgd' ,
                            'Total MC'   ,
                            'Data'       ,
                            'Data/MC'    ,
                            'Purity'     , 
                            'RelEff'     , 
                            'Eff'
                            ])
        i = 0
        nTrueSig = 0
        previousSig = 0

        for row in self.rows:
            if (i == 0):
                nTrueSig = row.GetSig()
            else:
                previousSig = self.rows[i - 1].GetSig()


                other = row.GetTotalBkgd() - (row.GetQE()  + 
                                              row.GetRES() + 
                                              row.GetDIS() + 
                                              row.GetMEC() + 
                                              row.GetNC() )

                purity = (row.GetSig()/(row.GetSig() + row.GetTotalBkgd()))*100

                table_data.append([ row.GetName()                              ,                           
                                    round(row.GetSig()      , 2)               ,                           
                                    round(row.GetQE()       , 2)               ,                           
                                    round(row.GetRES()      , 2)               ,                           
                                    round(row.GetDIS()      , 2)               ,                           
                                    round(row.GetMEC()      , 2)               ,                           
                                    round(row.GetNC()       , 2)               ,                           
                                    round(other             , 2)               ,                           
                                    round(row.GetTotalBkgd(), 2)               ,                           
                                    round(row.GetTotalMC()  , 2)               ,                           
                                    row.GetData()                              ,                           
                                    round((row.GetData()/row.GetTotalMC()), 2) ,
                                    round(purity            , 2)               ,    
                                    round((row.GetSig()/previousSig)*100  , 2) ,
                                    round((row.GetSig()/nTrueSig)*100     , 2) 
                                ])
            i += 1
        table = AsciiTable(table_data,title=self.title)
        print(table.table)

    def SaveCSV(self):
        with open(self.csvName, "w", newline='') as csvfile:
            fieldnames = [  'Cut Name'   , 
                            'CC COH'     , 
                            'CC QE'      , 
                            'CC RES'     , 
                            'CC DIS'     , 
                            'CC MEC'     , 
                            'NC'         , 
                            'Other'      , 
                            'Total Bkgd' ,
                            'Total MC'   ,
                            'Data'       ,
                            'Data/MC'    ,
                            'Purity'     , 
                            'RelEff'     , 
                            'Eff'
                            ]
            
            writer     = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            i = 0
            nTrueSig = 0
            previousSig = 0

            for row in self.rows:
                if (i == 0):
                    nTrueSig = row.GetSig()
                else:
                    previousSig = self.rows[i - 1].GetSig()


                    other = row.GetTotalBkgd() - (  row.GetQE()  + 
                                                    row.GetRES() + 
                                                    row.GetDIS() + 
                                                    row.GetMEC() + 
                                                    row.GetNC() )

                    purity = (row.GetSig()/(row.GetSig() + row.GetTotalBkgd()))*100

                    writer.writerow({   'Cut Name'   : row.GetName()                                ,                                                                                                         
                                        'CC COH'     : round(row.GetSig()      , 2)                 ,                                                                                                        
                                        'CC QE'      : round(row.GetQE()       , 2)                 ,                                                                                                        
                                        'CC RES'     : round(row.GetRES()      , 2)                 ,                                                                                                        
                                        'CC DIS'     : round(row.GetDIS()      , 2)                 ,                                                                                                        
                                        'CC MEC'     : round(row.GetMEC()      , 2)                 ,                                                                                                        
                                        'NC'         : round(row.GetNC()       , 2)                 ,                                                                                                        
                                        'Other'      : round(other             , 2)                 ,                                                                                                        
                                        'Total Bkgd' : round(row.GetTotalBkgd(), 2)                 ,                                                                                                        
                                        'Total MC'   : round(row.GetTotalMC()  , 2)                 ,                                                                                                        
                                        'Data'       : row.GetData()                                ,                                                                                                        
                                        'Data/MC'    : round((row.GetData()/row.GetTotalMC()), 2)   ,
                                        'Purity'     : round(purity            , 2)                 ,
                                        'RelEff'     : round((row.GetSig()/previousSig)*100  , 2)   ,
                                        'Eff'        : round((row.GetSig()/nTrueSig)*100     , 2)                  
                                    })

                i += 1
            csvfile.close()
       

class CutTable:
    """Creates blue print of cut table

    Returns:
        _type_: _description_
    """
    def __init__(self, csvName, title, rows):
        """Input arguments for constructor

        Args:
            csvName (string): Name of the csv file
            titleName (string): Title of the table
            rows (list): list of CutTable rows
        """     
        self.row1 = rows[0]
        self.row2 = rows[1]
        self.row3 = rows[2]
        self.row4 = rows[3]
        self.row5 = rows[4]
        self.csvName = csvName
        self.title = title

    def GetRow1(self):
        """Returns row1

        Returns:
            CutTableRow: returns row1 information
        """
        return self.row1

    def GetRow2(self):
        """Returns row2

        Returns:
            CutTableRow: returns row2 information
        """
        return self.row2

    def GetRow3(self):
        """Returns row3

        Returns:
            CutTableRow: returns row3 information
        """
        return self.row3

    def GetRow4(self):
        """Returns row4

        Returns:
            CutTableRow: returns row4 information
        """
        return self.row4

    def GetRow5(self):
        """Returns row5

        Returns:
            CutTableRow: returns row5 information
        """
        return self.row5

    def PrintTable(self):
        """Prints cut table to the Terminal
        """
        table_data = []
        table_data.append(['Cut Name'    , 
                            'CC COH'     , 
                            'CC QE'      , 
                            'CC RES'     , 
                            'CC DIS'     , 
                            'CC MEC'     , 
                            'NC'         , 
                            'Other'      , 
                            'Total Bkgd' ,
                            'Total MC'   ,
                            'Data'       ,
                            'Data/MC'    ,
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'
                            ])

        other = self.GetRow1().GetTotalBkgd() - (self.GetRow1().GetQE() + self.GetRow1().GetRES() + self.GetRow1().GetDIS() + self.GetRow1().GetMEC() + self.GetRow1().GetNC() )

        table_data.append([self.GetRow1().GetName()                ,                           
                           round(self.GetRow1().GetSig()      , 2) ,                           
                           round(self.GetRow1().GetQE()       , 2) ,                           
                           round(self.GetRow1().GetRES()      , 2) ,                           
                           round(self.GetRow1().GetDIS()      , 2) ,                           
                           round(self.GetRow1().GetMEC()      , 2) ,                           
                           round(self.GetRow1().GetNC()       , 2) ,                           
                           round(other                        , 2) ,                           
                           round(self.GetRow1().GetTotalBkgd(), 2) ,                           
                           round(self.GetRow1().GetTotalMC()  , 2) ,                           
                           self.GetRow1().GetData()                ,                           
                           round((self.GetRow1().GetData()/self.GetRow1().GetTotalMC()), 2)
                        #0                                                ,    
                        #0                                                ,    
                        #0
                        ])

        other = self.GetRow2().GetTotalBkgd() - (self.GetRow2().GetQE() + self.GetRow2().GetRES() + self.GetRow2().GetDIS() + self.GetRow2().GetMEC() + self.GetRow2().GetNC() )

        table_data.append([self.GetRow2().GetName()                ,                           
                           round(self.GetRow2().GetSig()      , 2) ,                           
                           round(self.GetRow2().GetQE()       , 2) ,                           
                           round(self.GetRow2().GetRES()      , 2) ,                           
                           round(self.GetRow2().GetDIS()      , 2) ,                           
                           round(self.GetRow2().GetMEC()      , 2) ,                           
                           round(self.GetRow2().GetNC()       , 2) ,                           
                           round(other                        , 2) ,                           
                           round(self.GetRow2().GetTotalBkgd(), 2) ,                           
                           round(self.GetRow2().GetTotalMC()  , 2) ,                           
                           self.GetRow2().GetData()                ,                           
                           round((self.GetRow2().GetData()/self.GetRow2().GetTotalMC()), 2)
                        #0                                                ,    
                        #0                                                ,    
                        #0
                        ])

        other = self.GetRow3().GetTotalBkgd() - (self.GetRow3().GetQE() + self.GetRow3().GetRES() + self.GetRow3().GetDIS() + self.GetRow3().GetMEC() + self.GetRow3().GetNC() )

        table_data.append([self.GetRow3().GetName()                ,                           
                           round(self.GetRow3().GetSig()      , 2) ,                           
                           round(self.GetRow3().GetQE()       , 2) ,                           
                           round(self.GetRow3().GetRES()      , 2) ,                           
                           round(self.GetRow3().GetDIS()      , 2) ,                           
                           round(self.GetRow3().GetMEC()      , 2) ,                           
                           round(self.GetRow3().GetNC()       , 2) ,                           
                           round(other                        , 2) ,                           
                           round(self.GetRow3().GetTotalBkgd(), 2) ,                           
                           round(self.GetRow3().GetTotalMC()  , 2) ,                           
                           self.GetRow3().GetData()                ,                           
                           round((self.GetRow3().GetData()/self.GetRow3().GetTotalMC()), 2)
                        #0                                                ,    
                        #0                                                ,    
                        #0
                        ])

        other = self.GetRow4().GetTotalBkgd() - (self.GetRow4().GetQE() + self.GetRow4().GetRES() + self.GetRow4().GetDIS() + self.GetRow4().GetMEC() + self.GetRow4().GetNC() )

        table_data.append([self.GetRow4().GetName()                ,                           
                           round(self.GetRow4().GetSig()      , 2) ,                           
                           round(self.GetRow4().GetQE()       , 2) ,                           
                           round(self.GetRow4().GetRES()      , 2) ,                           
                           round(self.GetRow4().GetDIS()      , 2) ,                           
                           round(self.GetRow4().GetMEC()      , 2) ,                           
                           round(self.GetRow4().GetNC()       , 2) ,                           
                           round(other                        , 2) ,                           
                           round(self.GetRow4().GetTotalBkgd(), 2) ,                           
                           round(self.GetRow4().GetTotalMC()  , 2) ,                           
                           self.GetRow4().GetData()                ,                           
                           round((self.GetRow4().GetData()/self.GetRow4().GetTotalMC()), 2)
                        #0                                                ,    
                        #0                                                ,    
                        #0
                        ])

        other = self.GetRow5().GetTotalBkgd() - (self.GetRow5().GetQE() + self.GetRow5().GetRES() + self.GetRow5().GetDIS() + self.GetRow5().GetMEC() + self.GetRow5().GetNC() )

        table_data.append([self.GetRow5().GetName()                ,                           
                           round(self.GetRow5().GetSig()      , 2) ,                           
                           round(self.GetRow5().GetQE()       , 2) ,                           
                           round(self.GetRow5().GetRES()      , 2) ,                           
                           round(self.GetRow5().GetDIS()      , 2) ,                           
                           round(self.GetRow5().GetMEC()      , 2) ,                           
                           round(self.GetRow5().GetNC()       , 2) ,                           
                           round(other                        , 2) ,                           
                           round(self.GetRow5().GetTotalBkgd(), 2) ,                           
                           round(self.GetRow5().GetTotalMC()  , 2) ,                           
                           self.GetRow5().GetData()                ,                           
                           round((self.GetRow5().GetData()/self.GetRow5().GetTotalMC()), 2)
                        #0                                                ,    
                        #0                                                ,    
                        #0
                        ])

        table = AsciiTable(table_data,title=self.title)
        print(table.table)

    def SaveCSV(self):
        with open(self.csvName, "w", newline='') as csvfile:
            fieldnames = [  'Cut Name'   , 
                            'CC COH'     , 
                            'CC QE'      , 
                            'CC RES'     , 
                            'CC DIS'     , 
                            'CC MEC'     , 
                            'NC'         , 
                            'Other'      , 
                            'Total Bkgd' ,
                            'Total MC'   ,
                            'Data'       ,
                            'Data/MC'    ,
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'
                            ]
            
            writer     = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            other = self.GetRow1().GetTotalBkgd() - (self.GetRow1().GetQE() + self.GetRow1().GetRES() + self.GetRow1().GetDIS() + self.GetRow1().GetMEC() + self.GetRow1().GetNC() )

            writer.writerow({ 'Cut Name'   : self.GetRow1().GetName()                  ,                                                                                                         
                            'CC COH'     : round(self.GetRow1().GetSig()      , 2)     ,                                                                                                        
                            'CC QE'      : round(self.GetRow1().GetQE()       , 2)     ,                                                                                                        
                            'CC RES'     : round(self.GetRow1().GetRES()      , 2)     ,                                                                                                        
                            'CC DIS'     : round(self.GetRow1().GetDIS()      , 2)     ,                                                                                                        
                            'CC MEC'     : round(self.GetRow1().GetMEC()      , 2)     ,                                                                                                        
                            'NC'         : round(self.GetRow1().GetNC()       , 2)     ,                                                                                                        
                            'Other'      : round(other                        , 2)     ,                                                                                                        
                            'Total Bkgd' : round(self.GetRow1().GetTotalBkgd(), 2)     ,                                                                                                        
                            'Total MC'   : round(self.GetRow1().GetTotalMC()  , 2)     ,                                                                                                        
                            'Data'       : self.GetRow1().GetData()                    ,                                                                                                        
                            'Data/MC'    : round((self.GetRow1().GetData()/self.GetRow1().GetTotalMC()), 2)
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'                            
                            })

            writer.writerow({ 'Cut Name'   : self.GetRow2().GetName()                  , 
                            'CC COH'     : round(self.GetRow2().GetSig()      , 2)     ,
                            'CC QE'      : round(self.GetRow2().GetQE()       , 2)     ,
                            'CC RES'     : round(self.GetRow2().GetRES()      , 2)     ,
                            'CC DIS'     : round(self.GetRow2().GetDIS()      , 2)     ,
                            'CC MEC'     : round(self.GetRow2().GetMEC()      , 2)     ,
                            'NC'         : round(self.GetRow2().GetNC()       , 2)     ,
                            'Other'      : round(other                        , 2)     ,
                            'Total Bkgd' : round(self.GetRow2().GetTotalBkgd(), 2)     ,
                            'Total MC'   : round(self.GetRow2().GetTotalMC()  , 2)     ,
                            'Data'       : self.GetRow2().GetData()                    ,
                            'Data/MC'    : round((self.GetRow2().GetData()/self.GetRow2().GetTotalMC()), 2)
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'                            
                            })

            writer.writerow({ 'Cut Name'   : self.GetRow3().GetName()                  , 
                            'CC COH'     : round(self.GetRow3().GetSig()      , 2)     ,
                            'CC QE'      : round(self.GetRow3().GetQE()       , 2)     ,
                            'CC RES'     : round(self.GetRow3().GetRES()      , 2)     ,
                            'CC DIS'     : round(self.GetRow3().GetDIS()      , 2)     ,
                            'CC MEC'     : round(self.GetRow3().GetMEC()      , 2)     ,
                            'NC'         : round(self.GetRow3().GetNC()       , 2)     ,
                            'Other'      : round(other                        , 2)     ,
                            'Total Bkgd' : round(self.GetRow3().GetTotalBkgd(), 2)     ,
                            'Total MC'   : round(self.GetRow3().GetTotalMC()  , 2)     ,
                            'Data'       : self.GetRow3().GetData()                    ,
                            'Data/MC'    : round((self.GetRow3().GetData()/self.GetRow3().GetTotalMC()), 2)
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'                            
                            })

            writer.writerow({ 'Cut Name'   : self.GetRow4().GetName()                , 
                            'CC COH'     : round(self.GetRow4().GetSig()      , 2)   ,
                            'CC QE'      : round(self.GetRow4().GetQE()       , 2)   ,
                            'CC RES'     : round(self.GetRow4().GetRES()      , 2)   ,
                            'CC DIS'     : round(self.GetRow4().GetDIS()      , 2)   ,
                            'CC MEC'     : round(self.GetRow4().GetMEC()      , 2)   ,
                            'NC'         : round(self.GetRow4().GetNC()       , 2)   ,
                            'Other'      : round(other                        , 2)   ,
                            'Total Bkgd' : round(self.GetRow4().GetTotalBkgd(), 2)   ,
                            'Total MC'   : round(self.GetRow4().GetTotalMC()  , 2)   ,
                            'Data'       : self.GetRow4().GetData()                  ,
                            'Data/MC'    : round((self.GetRow4().GetData()/self.GetRow4().GetTotalMC()), 2)
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'                            
                            })

            writer.writerow({ 'Cut Name'   : self.GetRow5().GetName()                , 
                            'CC COH'     : round(self.GetRow5().GetSig()      , 2)   ,
                            'CC QE'      : round(self.GetRow5().GetQE()       , 2)   ,
                            'CC RES'     : round(self.GetRow5().GetRES()      , 2)   ,
                            'CC DIS'     : round(self.GetRow5().GetDIS()      , 2)   ,
                            'CC MEC'     : round(self.GetRow5().GetMEC()      , 2)   ,
                            'NC'         : round(self.GetRow5().GetNC()       , 2)   ,
                            'Other'      : round(other                        , 2)   ,
                            'Total Bkgd' : round(self.GetRow5().GetTotalBkgd(), 2)   ,
                            'Total MC'   : round(self.GetRow5().GetTotalMC()  , 2)   ,
                            'Data'       : self.GetRow5().GetData()                  ,
                            'Data/MC'    : round((self.GetRow5().GetData()/self.GetRow5().GetTotalMC()), 2)
                            #'Purity'     , 
                            #'RelEff'     , 
                            #'Eff'                            
                            })

            csvfile.close()




    






class CutTableRow:
    """Create blue print of cut table row
    """
    def __init__(self, cutName, nSig, nQE, nRES, nDIS, nMEC, nNC, ntotBkgd, ntotMC, nData ):
        """Input arguments of the constructor

        Args:
            cutName (string): Name of the cut
            nSig (double): Number of Signal Events
            nQE (double): Number of CCQE Events
            nRES (double): Number of CCRES Events
            nDIS (double): Number of CCDIS Events
            nMEC (double): Number of CCMEC Events
            nNC (double): Number of NC Events
            ntotBkgd (double): Number of Total Background Events
            ntotMC (double): Number of Total MC Events
            nData (double): Number of Data Events

        Returns:
            self: returns self object
        """
        self.cutName    = cutName
        self.nSig       = nSig
        self.nQE        = nQE
        self.nRES       = nRES
        self.nDIS       = nDIS
        self.nMEC       = nMEC
        self.nNC        = nNC
        self.ntotBkgd   = ntotBkgd
        self.ntotMC     = ntotMC
        self.nData      = nData

    def GetName(self):
        """Returns Cut Name

        Returns:
            string: returns cut name
        """
        return self.cutName

    def GetSig(self):
        """Returns number of signal events

        Returns:
            double: number of signal events
        """
        return self.nSig

    def GetQE(self):
        """Returns number of CCQE Events

        Returns:
            double: number of CCQE events
        """
        return self.nQE

    def GetRES(self):
        """Returns number of CCRES Events

        Returns:
            double: number of CCRES events
        """
        return self.nRES

    def GetDIS(self):
        """Returns number of CCDIS Events

        Returns:
            double: number of CCDIS Events
        """
        return self.nDIS

    def GetMEC(self):
        """Returns number of CCMEC Events

        Returns:
            double: number of CCMEC Events
        """
        return self.nMEC

    def GetNC(self):
        """Returns total number of NC Events

        Returns:
            double: number of NC Events
        """
        return self.nNC

    def GetTotalBkgd(self):
        """Returns total Background Events

        Returns:
            double: total Background Events
        """
        return self.ntotBkgd

    def GetTotalMC(self):
        """Returns total MC Events

        Returns:
            double: returns total MC events
        """
        return self.ntotMC

    def GetData(self):
        """Returns total data Events

        Returns:
            double: returns total data events
        """
        return self.nData



class ResolutionHists:
    def __init__(self):
        pass


class FillHists:
    """Create Necessary Histograms for data, MC signal/background
    """
    def __init__(self, tree, histInfo):
        """Create Necessary Histograms for data, MC signal/background

        Args:
            tree (TTree): TTree required to iterate
            histInfo (python list): list of TH1 parameters [name, title, nbins, Xmin, Xmax]
        """
        self.tree     = tree
        self.histInfo = histInfo

    def FillHists(self, isBackgroundRegion):
        if (isBackgroundRegion):
            pionIDHist = ROOT.TH1D(f"{self.histInfo[0]}_PionID", # Hist Name 
                                   f"{self.histInfo[1]}",        # Hits Title
                                      self.histInfo[2]  ,        # Number of Bins
                                      self.histInfo[3]  ,        # Xmin
                                      self.histInfo[4])          # Xmax

            hitIDHist = ROOT.TH1D(f"{self.histInfo[0]}_HitID", # Hist Name 
                                  f"{self.histInfo[1]}",        # Hits Title
                                     self.histInfo[2]  ,        # Number of Bins
                                     self.histInfo[3]  ,        # Xmin
                                     self.histInfo[4])          # Xmax

            kinematicIDHist = ROOT.TH1D(f"{self.histInfo[0]}_KinematicID", # Hist Name 
                                        f"{self.histInfo[1]}",        # Hits Title
                                           self.histInfo[2]  ,        # Number of Bins
                                           self.histInfo[3]  ,        # Xmin
                                           self.histInfo[4])          # Xmax

            pionIDHist.     SetDirectory(0)
            hitIDHist.      SetDirectory(0)
            kinematicIDHist.SetDirectory(0)

            for event in self.tree:
                muonID      = getattr(event, "BestKalmanMuonID" )
                pionID      = getattr(event, "FinalPionID"      )
                hitID       = getattr(event, "FinalHitScore"    )
                kinematicID = getattr(event, "NewKinematicScore")
                recoT       = getattr(event, "RecoTKalman"      )

                if ( getattr(event, "BestKalmanMuonID" ) >  0.615 and getattr(event, "RecoTKalman") >= 0 and getattr(event, "RecoTKalman"      ) <  0.2):
                    if (getattr(event, "FinalHitScore") < 0.46 or getattr(event, "NewKinematicScore") < 0.84):
                        pionIDHist.Fill(pionID)

                    if ((pionID < 0.3 or kinematicID < 0.84)):
                        hitIDHist.Fill(hitID)

                    if ((pionID < 0.05 or hitID < 0.05)):
                        kinematicIDHist.Fill(kinematicID)
        return [pionIDHist, hitIDHist, kinematicIDHist]


    

    

    




class FigOfMerits:
    def __init__(self, sigHist, backHist):
        self.SigHist  = sigHist
        self.BackHist = backHist

    def GetSensitivityHist(self):
        nBins = self.SigHist.GetNbinsX()
        xMin  = self.SigHist.GetXaxis().GetXmin()
        xMax  = self.SigHist.GetXaxis().GetXmax()
        
        #print(nBins, xMin, xMax)
        #cumSigHist = ROOT.TH1D("hist", "", nBins, xMin, xMax)
        hist       = ROOT.TH1D("hist", "", nBins, xMin, xMax)

        #cumSigHist.SetDirectory(0)
        hist.SetDirectory(0)


        total = 0
        for i in range(1, nBins + 1):
            sig  = self.SigHist.Integral(i, nBins)
            back = self.BackHist.Integral(i, nBins)
            if ((sig + back) == 0):
                hist.SetBinContent(i, 0)
            else:
                hist.SetBinContent(i, sig/sqrt(sig + back))

        return hist

    def GetPurityHist(self):
        nBins = self.SigHist.GetNbinsX()
        xMin  = self.SigHist.GetXaxis().GetXmin()
        xMax  = self.SigHist.GetXaxis().GetXmax()
        
        #print(nBins, xMin, xMax)
        #cumSigHist = ROOT.TH1D("hist", "", nBins, xMin, xMax)
        hist       = ROOT.TH1D("hist", "", nBins, xMin, xMax)

        #cumSigHist.SetDirectory(0)
        hist.SetDirectory(0)

        total = 0
        for i in range(1, nBins + 1):
            sig  = self.SigHist.Integral(i, nBins)
            back = self.BackHist.Integral(i, nBins)
            if ((sig + back) == 0):
                hist.SetBinContent(i, 0)
            else:
                hist.SetBinContent(i, sig/(sig + back))

        return hist

    def GetSignalEfficiencyHist(self):
        nBins = self.SigHist.GetNbinsX()
        xMin  = self.SigHist.GetXaxis().GetXmin()
        xMax  = self.SigHist.GetXaxis().GetXmax()
        
        #print(nBins, xMin, xMax)
        #cumSigHist = ROOT.TH1D("hist", "", nBins, xMin, xMax)
        hist       = ROOT.TH1D("hist", "", nBins, xMin, xMax)

        #cumSigHist.SetDirectory(0)
        hist.SetDirectory(0)

        total = self.SigHist.Integral(1, -1)
        for i in range(1, nBins + 1):
            sigEff = self.SigHist.Integral(i, nBins)/total
            hist.SetBinContent(i, sigEff)

        return hist

    def GetBackgroundEfficiencyHist(self):
        nBins = self.BackHist.GetNbinsX()
        xMin  = self.BackHist.GetXaxis().GetXmin()
        xMax  = self.BackHist.GetXaxis().GetXmax()
    
        #print(nBins, xMin, xMax)
        #cumbackHist = ROOT.TH1D("hist", "", nBins, xMin, xMax)
        hist       = ROOT.TH1D("hist", "", nBins, xMin, xMax)

        #cumbackHist.SetDirectory(0)
        hist.SetDirectory(0)

        total = self.BackHist.Integral(1, -1)
        for i in range(1, nBins + 1):
            backEff = self.BackHist.Integral(i, nBins)/total
            hist.SetBinContent(i, backEff)

        return hist



class Prong:
    def __init__(self  ,
                 MuonID,
                 PionID,
                 Length,
                 CalE  ,
                 PID   ,
                 dir  ):
        self.MuonID = MuonID
        self.PionID = PionID
        self.Length = Length
        self.CalE   = CalE
        self.PID    = PID
        self.dir    = dir

    def GetMuonID(self):
        return self.MuonID
    
    def GetPionID(self):
        return self.PionID

    def GetLength(self):
        return self.Length

    def GetCalE(self):
        return self.CalE

    def GetDirection(self):
        return self.dir

    def GetPID(self):
        return self.PID

class MuonInfo:
    def __init__(self     ,
                 nKalman  ,
                 LenInAct ,
                 LenInCat ,
                 DirX     ,
                 DirY     ,
                 DirZ     ):
        self.nKalman  = nKalman
        self.LenInAct = LenInAct
        self.LenInCat = LenInCat
        self.DirX     = DirX
        self.DirY     = DirY
        self.DirZ     = DirZ


    def GetNTracks(self):
        return self.nKalman

    def GetLenInAct(self):
        return self.LenInAct

    def GetLenInCat(self):
        return self.LenInCat

    def GetDirX(self):
        return self.DirX

    def GetDirY(self):
        return self.DirY

    def GetDirZ(self):
        return self.DirZ

    

class PionInfo:
    def __init__(self         ,
                 nTracks      ,
                 muonOverlapE ,
                 slcCalE      ,
                 muonCalE     ,
                 pionPngKEReg ,
                 pngDirX      ,
                 pngDirY      ,
                 pngDirZ      ,
                 trkDirX      ,
                 trkDirY      ,
                 trkDirZ      ):
        self.MuonOverlapE = muonOverlapE
        self.SlcCalE      = slcCalE
        self.MuonCalE     = muonCalE
        self.nTracks      = nTracks
        self.PionPngKE    = pionPngKEReg
        self.pngDirX      = pngDirX
        self.pngDirY      = pngDirY
        self.pngDirZ      = pngDirZ
        self.trkDirX      = trkDirX
        self.trkDirY      = trkDirY
        self.trkDirZ      = trkDirZ

    def GetNTracks(self):
        return self.nTracks

    def GetMuonOverlapE(self):
        return self.MuonOverlapE

    def GetSlcCalE(self):
        return self.SlcCalE

    def GetMuonCalE(self):
        return self.MuonCalE

    def GetPionPngKE(self):
        return self.PionPngKE

    def GetTrackDirX(self):
        return self.trkDirX

    def GetTrackDirY(self):
        return self.trkDirY

    def GetTrackDirZ(self):
        return self.trkDirZ

    def GetProngDirX(self):
        return self.pngDirX

    def GetProngDirY(self):
        return self.pngDirY

    def GetProngDirZ(self):
        return self.pngDirZ



    

class Track:
    def __init__(self  ,
                 MuonID,
                 Length,
                 CalE  ,
                 TrueE ,
                 PID   ,
                 dir  ):
        self.MuonID = MuonID
        self.Length = Length
        self.CalE   = CalE
        self.TrueE  = TrueE
        self.PID    = PID
        self.dir    = dir

    def GetMuonID(self):
        return self.MuonID

    def GetLength(self):
        return self.Length

    def GetCalE(self):
        return self.CalE

    def GetTrueE(self):
        return self.TrueE

    def GetDirection(self):
        return self.dir

    def GetPID(self):
        return self.PID

# class CutTableRow:
#     def __init__(self, backTree, scale):
#         self.backTree = backTree
#         self.scale    = scale

#     def GetRow(self):
#         #self.sigEvents = self.sigTree.GetEntries()*self.scale
#         nQE               = 0
#         nRES              = 0
#         nDIS              = 0
#         nCOH              = 0
#         nCOHElastic       = 0
#         nElecScat         = 0
#         nIMDAnihilation   = 0
#         nInverseBetaDecay = 0
#         nGlaShowRes       = 0
#         nAMUGamma         = 0
#         nMEC              = 0
#         nDiffractive      = 0
#         nEM               = 0
#         nWeakMix          = 0
#         nBack             = 0
#         nNC               = 0
        
#         for event in self.backTree:
#             intType = getattr(event, "IntType")
#             IsCC    = getattr(event, "IsCC"   )
#             if ((IsCC == 1) and (intType  == 0)):
#                 nQE  += 1
#             if ((IsCC == 1) and (intType  == 1)):
#                 nRES += 1
#             if ((IsCC == 1) and (intType  == 2)):
#                 nDIS += 1
#             if ((IsCC == 1) and (intType  == 3)):
#                 nCOH += 1
#             if ((IsCC == 1) and (intType  == 4)):
#                 nCOHElastic += 1
#             if ((IsCC == 1) and (intType  == 5)):
#                 nElecScat += 1
#             if ((IsCC == 1) and (intType  == 6)):
#                 nIMDAnihilation += 1
#             if ((IsCC == 1) and (intType  == 7)):
#                 nInverseBetaDecay += 1
#             if ((IsCC == 1) and (intType  == 8)):
#                 nGlaShowRes += 1
#             if ((IsCC == 1) and (intType  == 9)):
#                 nAMUGamma += 1
#             if ((IsCC == 1) and (intType  == 10)):
#                 nMEC += 1
#             if ((IsCC == 1) and (intType  == 11)):
#                 nDiffractive += 1
#             if ((IsCC == 1) and (intType  == 12)):
#                 nEM += 1
#             if ((IsCC == 1) and (intType  == 13)):
#                 nWeakMix += 1
#             if (IsCC == 0):
#                 nNC += 1
            
#             nBack += 1
            

#         return [round((nQE               * self.scale), 2),  # 0
#                 round((nRES              * self.scale), 2),  # 1
#                 round((nDIS              * self.scale), 2),  # 2
#                 round((nCOH              * self.scale), 2),  # 3
#                 round((nCOHElastic       * self.scale), 2),  # 4
#                 round((nCOHElastic       * self.scale), 2),  # 5
#                 round((nElecScat         * self.scale), 2),  # 6
#                 round((nIMDAnihilation   * self.scale), 2),  # 7
#                 round((nInverseBetaDecay * self.scale), 2),  # 8
#                 round((nGlaShowRes       * self.scale), 2),  # 9
#                 round((nAMUGamma         * self.scale), 2),  # 10
#                 round((nMEC              * self.scale), 2),  # 11
#                 round((nDiffractive      * self.scale), 2),  # 12
#                 round((nEM               * self.scale), 2),  # 13
#                 round((nWeakMix          * self.scale), 2),  # 14
#                 round((nBack             * self.scale), 2),  # 15
#                 round((nNC               * self.scale), 2)]  # 16












class CreateParticleCandidateTable:
    def __init__(self, candidateList, particleName, csvFileName):
        self.Candidates   = candidateList
        self.ParticleName = particleName
        self.CSVFileName  = csvFileName


    def SaveCSVFile(self):
        particleCands = list(dict.fromkeys(self.Candidates))
        with open(self.CSVFileName, "w", newline='') as csvfile:
            fieldnames = [f"{self.ParticleName} Candidate", "Number of Events", "Percentage"]
            writer     = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for particleCand in particleCands:
                writer.writerow({f"{self.ParticleName} Candidate":particleCand, "Number of Events":self.Candidates.count(particleCand), "Percentage":round(((self.Candidates.count(particleCand))/(len(self.Candidates)))*100, 3)})

            csvfile.close()



    


class EventSelection:
    def __init__( self        , 
		          CutName     ,
                  IsMuonID    , 
                  IsPionID    , 
                  IsRecoT     , 
                  IsKinematic , 
                  IsHitInfo    ):

        self.IsMuonIDCut    = IsMuonID
        self.IsPionIDCut    = IsPionID
        self.IsTCut         = IsRecoT
        self.IsKinematicCut = IsKinematic
        self.IsHitInfo      = IsHitInfo
        self.CutName        = CutName

    def SetVariables(   self        ,
 	                    MuonLen     ,
                        MuonID      , 
		                PionCalE    , 
                        EstPionKE   , 
                        PionID      , 
                        RecoT       , 
                        Kinematic   , 
                        HitInfoScore ):

        self.MuonIDVal    = MuonID
        self.PionIDVal    = PionID
        self.recoTVal     = RecoT
        self.KinematicVal = Kinematic
        self.PionCalEVal  = PionCalE
        self.MuonLenVal   = MuonLen
        self.PionKEPol    = EstPionKE
        self.HitInfoScore = HitInfoScore


    # def SetThresholds(  self                            ,
    #                     vtxX                 = 0        ,
    #                     vtxY                 = 0        ,
    #                     vtxZ                 = 0        , 
	# 	                pionIDThreshold      = 0.7      , 
    #                     recoTThreshold       = [0, 0.2] ,
    #                     KinematicThreshold   = 0.72     ,
    #                     HiInfoScoreThreshold = 0.4      ):
        

    def SetThresholds(  self                ,
                        muonIDThreshold     , 
		                pionIDThreshold     , 
                        recoTThreshold      ,
                        KinematicThreshold  ,
                        HiInfoScoreThreshold):
        

        self.MuonIDThreshold       = muonIDThreshold
        self.PionIDThreshold       = pionIDThreshold
        self.recoTThreshold        = recoTThreshold
        self.KinematicThreshold    = KinematicThreshold
        self.HitInfoScoreThreshold = HiInfoScoreThreshold

    def GetName(self):
        return self.CutName

    def MuonIDCut(self):
        if ( self.MuonIDVal < self.MuonIDThreshold):
            return False
        else:
            return True


    def PionIDCut(self):
        if (self.PionIDVal > self.PionIDThreshold):
            return True
        else:
            return False
    
   
    def RecoTCut(self):
        if (self.recoTVal >= self.recoTThreshold[0] ):
            return True
        else:
            return False

    def KinematcCut(self):
        if (self.KinematicVal > self.KinematicThreshold):
            return True
        else:
            return False

    def HitInfoScoreCut(self):
        if (self.HitInfoScore > self.HitInfoScoreThreshold):
            return True
        else:
            return False
            

    def PionCalECut(self):
        if (self.PionCalEVal >= 0):
            return True
        else:
            return False

    def PionKECut(self):
        if (self.TruePionKE >= 0 and self.PionKEPol < 1.5):
            return True
        else:
            return False


    def MuonLenCut(self):
        if (self.MuonLenVal >= 0):
            return True
        else:
            return False


    def Output(self):

        if (    (self.IsMuonIDCut    == True ) and
                (self.IsPionIDCut    == True ) and
                (self.IsTCut         == True ) and 
                (self.IsKinematicCut == True ) and
                (self.IsHitInfo      == True) ):

            # return (self.PionCalECut         () and 
            #         self.MuonLenCut          () and 
            #         self.MuonIDCut           () and 
            #         self.PionIDCut           () and
            #         self.RecoTCut            () and
            #         self.KinematcCut         () and
            #         self.HitInfoScoreCut     () )

            return (self.PionCalECut         () and 
                    self.MuonLenCut          () and 
                    self.MuonIDCut           () and 
                    self.PionIDCut           () and
                    self.HitInfoScoreCut     () )

        if (    (self.IsMuonIDCut    == True ) and
                (self.IsPionIDCut    == True ) and
                (self.IsTCut         == True ) and 
                (self.IsKinematicCut == True ) and
                (self.IsHitInfo      == False) ):

            # return (self.PionCalECut         () and 
            #         self.MuonLenCut          () and 
            #         self.MuonIDCut           () and 
            #         self.PionIDCut           () and
            #         self.RecoTCut            () and
            #         self.KinematcCut         () )
            return (self.PionCalECut         () and 
                    self.MuonLenCut          () and 
                    self.MuonIDCut           () and 
                    self.PionIDCut           () and
                    self.HitInfoScoreCut     () and
                    self.RecoTCut            () and
                    self.KinematcCut         () )



        if (    (self.IsMuonIDCut    == True ) and
                (self.IsPionIDCut    == True ) and
                (self.IsTCut         == True ) and 
                (self.IsKinematicCut == False) and
                (self.IsHitInfo      == False) ):

            # return (self.PionCalECut         () and 
            #         self.MuonLenCut          () and 
            #         self.MuonIDCut           () and 
            #         self.PionIDCut           () and
            #         self.RecoTCut            () )

            return (self.PionCalECut         () and 
                    self.MuonLenCut          () and 
                    self.MuonIDCut           () and 
                    self.PionIDCut           () and
                    self.HitInfoScoreCut     () and
                    self.RecoTCut            () )



        if (    (self.IsMuonIDCut    == True ) and
                (self.IsPionIDCut    == True ) and
                (self.IsTCut         == False) and 
                (self.IsKinematicCut == False) and
                (self.IsHitInfo      == False) ):

            return (self.PionCalECut         () and 
                    self.MuonLenCut          () and 
                    self.MuonIDCut           () and 
                    self.PionIDCut           () )


        if (    (self.IsMuonIDCut    == True ) and
                (self.IsPionIDCut    == False) and
                (self.IsTCut         == False) and 
                (self.IsKinematicCut == False) and
                (self.IsHitInfo      == False) ):

            return (self.PionCalECut         () and 
                    self.MuonLenCut          () and 
                    self.MuonIDCut           () )

class CreateHist:
    def __init__(self, histDim, histName):
        self.hist       =   ROOT.TH1D(histName, "", histDim[0], histDim[1], histDim[2])
        self.hist.SetDirectory(0)
        self.hist.SetStats(0)


    def FillHist(self, var):
        self.hist.Fill(var)

    def GetHist(self):
        return self.hist

    def SetHistWidthAndColor(self, histInfo):
        self.hist.SetLineWidth(histInfo[0])
        self.hist.SetLineColor(histInfo[1])

class HitEPlot:
    def __init__(self, histInfo, title, legendInfo, fileName):
        self.histInfo      = histInfo
        self.title      = title
        self.legendInfo = legendInfo
        self.fileName   = fileName

        c   =   ROOT.TCanvas(title, title, 1024, 768)
        c.cd()

        l   =   ROOT.TLegend(legendInfo[0][0], legendInfo[0][1], legendInfo[0][2], legendInfo[0][3])
        i   =   0
        for hist in self.histInfo:
            hist[0].GetHist().SetLineColor(hist[1])
            hist[0].GetHist().SetLineWidth(2)
            hist[0].GetHist().GetXaxis().SetTitle("Hit Energy Deposition (GeV)")
            hist[0].GetHist().GetYaxis().SetTitle("Number of Events")
            hist[0].GetHist().GetYaxis().SetRangeUser(0, hist[3])



            hist[0].GetHist().Rebin(hist[2])
            hist[0].GetHist().Draw("hist same")
            l.AddEntry(hist[0].GetHist(), legendInfo[1][i], "l")
            i   +=  1

        l.Draw()

        c.SaveAs(fileName)

class SaveCanvas:
    """This Class is generated to save histograms in a canvas.
    """
    def __init__(self, hists, canvasParam, isSim):
        self.hists       = hists
        self.canvasParam = canvasParam
        self.IsSim       = isSim

    def SaveCanvas(self, leg):
        c = ROOT.TCanvas("c")
        c.cd()
        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.hists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)
            if ("Rect" in hist.GetName()):
                hist.Draw("E2 same")
            else:
                hist.Draw("hist same")

            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()

        if (self.IsSim):
            prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
            prelim.SetTextColor(921)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()

        else:
            prelim = ROOT.TLatex(.9, .95, "NOvA Preliminary")
            prelim.SetTextColor(4)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()



        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            l.AddEntry(hist, legName, "l")

        l.Draw()
        
        c.SaveAs(f"{self.canvasParam[6]}_Canvas.pdf")
        c.SaveAs(f"{self.canvasParam[6]}_Canvas.root")
        fOut = ROOT.TFile(f"{self.canvasParam[6]}_Objects.root","RECREATE")
        fOut.cd()
        c.Write()
        for hist in self.hists:
            hist.Write()

        fOut.Write()
        fOut.Close()

        c.Destructor()


    def SaveCanvasStatErrorBand(self, leg):
        c = ROOT.TCanvas("c")
        c.cd()
        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.hists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)
            if ("Stat" in hist.GetName()):
                #color = ROOT.gROOT.GetColor(hist.GetLineColor())
                color = hist.GetLineColor()
                print(f"LineColor: {color}")
                #newColor = ROOT.TColor(ROOT.TColor.GetFreeColorIndex(), color.GetRed(), color.GetGreen(),color.GetBlue())
                #newColor.SetAlpha(0.1)
                hist.SetFillColor(color)
                hist.SetMarkerColor(color)
                #hist.SetFillColorAlpha(color, 0.0)
                hist.Draw("E2")
            else:
                hist.Draw("hist same")

            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()

        if (self.IsSim):
            prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
            prelim.SetTextColor(921)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()

        else:
            prelim = ROOT.TLatex(.9, .95, "NOvA Preliminary")
            prelim.SetTextColor(4)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()



        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            l.AddEntry(hist, legName, "l")

        l.Draw()
        
        c.SaveAs(f"{self.canvasParam[6]}.pdf")
        c.SaveAs(f"{self.canvasParam[6]}.root")
        c.Destructor()





    def SaveCanvasWithErrors(self, leg):
        c = ROOT.TCanvas("c")
        c.cd()
        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.hists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)
            fit = ROOT.TF1("fit", "pol1", 0, 0.2)
            fit.SetLineColor(2)
            

            hist.Draw("hist E same")
            hist.Fit("fit")
            eq = fit.GetExpFormula()
            #fit.Draw("same")

            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()

        prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
        prelim.SetTextColor(921)
        prelim.SetNDC()
        prelim.SetTextSize(2 / 30.)
        prelim.SetTextAlign(32)
        prelim.Draw()

        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            l.AddEntry(hist, legName, "l")

        
        #l.AddEntry(fit, eq, "l")
        l.Draw()
        
        c.SaveAs(f"{self.canvasParam[6]}.pdf")
        c.SaveAs(f"{self.canvasParam[6]}.root")


    def SaveDATACanvas(self, leg, isSimulation):
        c = ROOT.TCanvas("c")
        c.cd()
        pad1 = ROOT . TPad ( " pad1 " ," pad1 " ,0 ,0.3 ,1 ,1)
        pad1.SetBottomMargin(0.05)
        pad1.Draw()
        pad1.cd()

        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.hists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)
            
            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)
            if ("data" in hist.GetName()):
                nBins = hist.GetNbinsX()
                print(f"data Histogram Name: {hist.GetName()}")
                dataCum = hist.Clone("dataHistCum")
                dataCum.SetDirectory(0)

                hist.Draw ( "PE same" )
                dataHist = hist.Clone("dataHist")
                dataHist.SetDirectory(0)
                
                ratioHist = hist.Clone("ratioHist")
                ratioHist.SetDirectory(0)
            else:
                hist.Draw("hist same")

                

            if (("total" in hist.GetName()) and ("_MC" in hist.GetName())):
                print(f"Total MC Histogram Name: {hist.GetName()}")
                totalMCHist = hist.Clone("totalMCHist")
                totalMCHist.SetDirectory(0)
                ratioHist.Divide(hist)
                ratioHistWithErrors = CalculateErrorOfRatioHist(dataHist, totalMCHist)

                nBins = hist.GetNbinsX()
                #ratioHist.SetDirectory(0)


            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()
        if (isSimulation == True):
            prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
            prelim.SetTextColor(921)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()
        else:
            prelim = ROOT.TLatex(.9, .95, "NOvA Preliminary")
            prelim.SetTextColor(4)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()

        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            if ("data" in hist.GetName()):
                l.AddEntry(hist, legName, "ep")
            else:
                l.AddEntry(hist, legName, "l")

        l.Draw()

        c.cd()
        pad2 = ROOT . TPad ( " pad2 " ," pad2 " ,0 ,0.05 ,1 ,0.3)
        pad2.SetTopMargin(0)
        pad2.Draw()
        pad2.cd ()

        
        ratioHistWithErrors.GetYaxis().SetLabelSize(0.12)
        ratioHistWithErrors.GetYaxis().SetTitleSize(0.12)
        ratioHistWithErrors.GetYaxis().SetTitle("Data/MC")
        ratioHistWithErrors.GetYaxis().SetTitleOffset(0.3)

        ratioHistWithErrors.GetXaxis().SetLabelSize(0.12)
        ratioHistWithErrors.GetXaxis().SetTitleSize(0.12)

        ratioHistWithErrors.Draw("pe")
        baseline = ROOT.TLine( self.canvasParam[0][0], 1, self.canvasParam[0][1], 1)
        baseline.Draw()

        c.SaveAs(f"{self.canvasParam[6]}.pdf")
        c.SaveAs(f"{self.canvasParam[6]}.root")
        c.Destructor()


    def SaveDATACanvasCumRatio(self, leg, isSimulation):
        c = ROOT.TCanvas("c")
        c.cd()
        pad1 = ROOT . TPad ( " pad1 " ," pad1 " ,0 ,0.3 ,1 ,1)
        pad1.SetBottomMargin(0.05)
        pad1.Draw()
        pad1.cd()

        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.hists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)
            if ("data" in hist.GetName()):
                nBins = hist.GetNbinsX()
                print(f"data Histogram Name: {hist.GetName()}")
                dataCum = hist.Clone("dataHistCum")

                for i in range(1, nBins+1):
                    dataCum.SetBinContent(i, hist.Integral(i, nBins))
                    binError = dataCum.GetBinContent(i)
                    dataCum.SetBinError(i, sqrt(binError))
                    #binError = hist.GetBinContent(i)
                    #hist.SetBinError(i, sqrt(binError))

                hist.Draw ( "PE same" )
                dataHist = hist.Clone("dataHist")
                dataHist.SetDirectory(0)
                
                ratioHist = hist.Clone("ratioHist")
                ratioHist.SetDirectory(0)
            else:
                hist.Draw("hist same")

                

            if (("total" in hist.GetName()) and ("_MC" in hist.GetName())):
                print(f"Total MC Histogram Name: {hist.GetName()}")
                totalMCHist = hist.Clone("totalMCHist")
                totalMCHist.SetDirectory(0)
                ratioHist.Divide(hist)
                ratioHistWithErrors = CalculateErrorOfRatioHist(dataHist, totalMCHist)

                totalCum = hist.Clone("toalMCHistCum")
                totalCum.SetDirectory(0)
                nBins = hist.GetNbinsX()
                for i in range(1, nBins+1):
                    totalCum.SetBinContent(i, hist.Integral(i, nBins))
                    binError = totalCum.GetBinContent(i)
                    totalCum.SetBinError(i, sqrt(binError))


                ratioCumHistWithErrors = CalculateErrorOfRatioHist(dataCum, totalCum)
                ratioCumHistWithErrors.SetDirectory(0)




                #ratioHist.SetDirectory(0)


            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()
        if (isSimulation == True):
            prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
            prelim.SetTextColor(921)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()
        else:
            prelim = ROOT.TLatex(.9, .95, "NOvA Preliminary")
            prelim.SetTextColor(4)
            prelim.SetNDC()
            prelim.SetTextSize(2 / 30.)
            prelim.SetTextAlign(32)
            prelim.Draw()

        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            if ("data" in hist.GetName()):
                l.AddEntry(hist, legName, "ep")
            else:
                l.AddEntry(hist, legName, "l")

        l.Draw()

        c.cd()
        pad2 = ROOT . TPad ( " pad2 " ," pad2 " ,0 ,0.05 ,1 ,0.3)
        pad2.SetTopMargin(0)
        pad2.Draw()
        pad2.cd ()

        
        ratioCumHistWithErrors.GetYaxis().SetLabelSize(0.12)
        ratioCumHistWithErrors.GetYaxis().SetTitleSize(0.12)
        ratioCumHistWithErrors.GetYaxis().SetTitle("Data/MC")
        ratioCumHistWithErrors.GetYaxis().SetTitleOffset(0.3)

        ratioCumHistWithErrors.GetXaxis().SetLabelSize(0.12)
        ratioCumHistWithErrors.GetXaxis().SetTitleSize(0.12)

        ratioCumHistWithErrors.Draw("pe")
        baseline = ROOT.TLine( self.canvasParam[0][0], 1, self.canvasParam[0][1], 1)
        baseline.Draw()

        c.SaveAs(f"{self.canvasParam[6]}Cum.pdf")
        c.SaveAs(f"{self.canvasParam[6]}Cum.root")
        c.Destructor()

    def SaveSystematicRatio(self, leg, IsCorr):
        if (len(self.hists)==3):
            print(len(self.hists))
            nominalHist = self.hists[1]
            upHist      = self.hists[0]
            downHist    = self.hists[2]

            nominalHist.SetDirectory(0)
            upHist.SetDirectory(0)
            downHist.SetDirectory(0)

            #nominalHist.Rebin(10)
            #upHist.Rebin(10)
            #downHist.Rebin(10)

            nominalRatio = nominalHist.Clone("nominalHistRatio")
            nominalRatio.SetDirectory(0)
            #nominalRatio.Rebin(10)
            nominalRatio.Divide(nominalHist)

            nominalRatio.SetLineColor(1)
            nominalRatio.SetLineWidth(2)

            #upRatio = upHist.Clone("upHistRatio")
            #upRatio.SetDirectory(0)
            #upRatio.Rebin(10)
            #upRatio.Divide(nominalHist)

            if (IsCorr):
                upRatio = CalculateErrorOfRatioHistFullyCorelated(upHist, nominalHist)
            else:
                upRatio = CalculateErrorOfRatioHist(upHist, nominalHist)
            upRatio.SetDirectory(0)

            upRatio.SetLineColor(2)
            upRatio.SetLineWidth(2)

            # downRatio = downHist.Clone("downHistRatio")
            # downRatio.SetDirectory(0)
            # #downRatio.Rebin(10)
            # downRatio.Divide(nominalHist)

            if (IsCorr):
                downRatio = CalculateErrorOfRatioHistFullyCorelated(downHist, nominalHist)
            else:
                downRatio = CalculateErrorOfRatioHist(downHist, nominalHist)

            downRatio.SetDirectory(0)

            downRatio.SetLineColor(4)
            downRatio.SetLineWidth(2)

            self.sysHists = [upRatio, nominalRatio, downRatio]
            #self.sysHists = [nominalRatio]

        if (len(self.hists)==2):
            print(len(self.hists))
            nominalHist = self.hists[0]
            upHist      = self.hists[1]

            nominalHist.SetDirectory(0)
            upHist.SetDirectory(0)

            #nominalHist.Rebin(10)
            #upHist.Rebin(10)

            nominalRatio = nominalHist.Clone("nominalHistRatio")
            nominalRatio.SetDirectory(0)
            #nominalRatio.Rebin(10)
            nominalRatio.Divide(nominalHist)

            nominalRatio.SetLineColor(1)
            nominalRatio.SetLineWidth(2)

            upRatio = upHist.Clone("upHistRatio")
            upRatio.SetDirectory(0)
            #upRatio.Rebin(10)
            upRatio.Divide(nominalHist)

            if (IsCorr):
                upRatio = CalculateErrorOfRatioHistFullyCorelated(upHist, nominalHist)
            else:
                upRatio = CalculateErrorOfRatioHist(upHist, nominalHist)
            upRatio.SetDirectory(0)

            upRatio.SetLineColor(2)
            upRatio.SetLineWidth(2)

            self.sysHists = [upRatio, nominalRatio]
            #self.sysHists = [nominalRatio]

        c = ROOT.TCanvas("c")
        c.cd()
        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.sysHists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            # if ("_mc_" in hist.GetName()):
            #     nbins = hist.GetNbinsX()
            #     xmin  = hist.GetXaxis().GetXmin()
            #     xmax  = hist.GetXaxis().GetXmax()
            #     nominalHist = ROOT.TH1D(f"{hist.GetName()}_normalized", "", nbins, xmin, xmax)


            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)

            hist.Draw("hist E same")

            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()

        prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
        prelim.SetTextColor(921)
        prelim.SetNDC()
        prelim.SetTextSize(2 / 30.)
        prelim.SetTextAlign(32)
        prelim.Draw()

        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            l.AddEntry(hist, legName, "l")

        l.Draw()
        
        c.SaveAs(f"{self.canvasParam[6]}Ratio.pdf")
        c.SaveAs(f"{self.canvasParam[6]}Ratio.root")

    def SaveCumulativeSystematicRatio(self, leg, IsCorr, IsIntToInf):
        if (len(self.hists)==3):
            print(len(self.hists))
            nominalHist = self.hists[1]
            upHist      = self.hists[0]
            downHist    = self.hists[2]

            nominalHist.SetDirectory(0)
            upHist.SetDirectory(0)
            downHist.SetDirectory(0)

            #nominalHist.Rebin(10)
            #upHist.Rebin(10)
            #downHist.Rebin(10)

            nominalRatio = nominalHist.Clone("nominalHistRatio")
            nominalRatio.SetDirectory(0)
            
            nominalCum = CreateCumulativePlot(nominalHist)
            nominalCum.SetDirectory(0)

            nominalCumRatio = nominalCum.Clone("nominalCumRatio")
            nominalCumRatio.SetDirectory(0)
            nominalCumRatio.Divide(nominalCum)

            upCum = CreateCumulativePlot(upHist)
            upCum.SetDirectory(0)

            upCumRatio = upCum.Clone("upCumRatio")
            upCumRatio.SetDirectory(0)
            upCumRatio.Divide(nominalCum)

            downCum = CreateCumulativePlot(downHist)
            downCum.SetDirectory(0)

            downCumRatio = downCum.Clone("downCumRatio")
            downCumRatio.SetDirectory(0)
            downCumRatio.Divide(nominalCum)


            #nominalRatio.Rebin(10)
            nominalRatio.Divide(nominalHist)

            nominalRatio.SetLineColor(1)
            nominalRatio.SetLineWidth(2)

            #upRatio = upHist.Clone("upHistRatio")
            #upRatio.SetDirectory(0)
            #upRatio.Rebin(10)
            #upRatio.Divide(nominalHist)

            if (IsCorr):
                upRatio = CalculateErrorOfRatioHistFullyCorelated(upCum, nominalCum)
            else:
                upRatio = CalculateErrorOfRatioHist(upCum, nominalCum)
            upRatio.SetDirectory(0)

            upRatio.SetLineColor(2)
            upRatio.SetLineWidth(2)

            # downRatio = downHist.Clone("downHistRatio")
            # downRatio.SetDirectory(0)
            # #downRatio.Rebin(10)
            # downRatio.Divide(nominalHist)

            if (IsCorr):
                downRatio = CalculateErrorOfRatioHistFullyCorelated(downCum, nominalCum)
            else:
                downRatio = CalculateErrorOfRatioHist(downCum, nominalCum)

            downRatio.SetDirectory(0)

            downRatio.SetLineColor(4)
            downRatio.SetLineWidth(2)

            self.sysHists = [upRatio, nominalRatio, downRatio]
            #self.sysHists = [nominalRatio]

        if (len(self.hists)==2):
            print(len(self.hists))
            nominalHist = self.hists[0]
            upHist      = self.hists[1]

            nominalHist.SetDirectory(0)
            upHist.SetDirectory(0)

            #nominalHist.Rebin(10)
            #upHist.Rebin(10)

            nominalRatio = nominalHist.Clone("nominalHistRatio")
            nominalRatio.SetDirectory(0)
            #nominalRatio.Rebin(10)
            nominalRatio.Divide(nominalHist)

            nominalRatio.SetLineColor(1)
            nominalRatio.SetLineWidth(2)

            upRatio = upHist.Clone("upHistRatio")
            upRatio.SetDirectory(0)
            #upRatio.Rebin(10)
            upRatio.Divide(nominalHist)

            upCum = CreateCumulativePlot(upHist)
            upCum.SetDirectory(0)

            nominalCum = CreateCumulativePlot(nominalHist)
            nominalCum.SetDirectory(0)

            if (IsCorr):
                upRatio = CalculateErrorOfRatioHistFullyCorelated(upCum, nominalCum)
            else:
                upRatio = CalculateErrorOfRatioHist(upCum, nominalCum)
            upRatio.SetDirectory(0)

            upRatio.SetLineColor(2)
            upRatio.SetLineWidth(2)

            self.sysHists = [upRatio, nominalRatio]
            #self.sysHists = [nominalRatio]

        c = ROOT.TCanvas("c")
        c.cd()
        if (leg[5] == True):
            c.SetGrid()
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        for hist in self.sysHists:
            #hist.SetLineColor(self.canvasParam[0])
            #hist.SetLineWidth(self.canvasParam[1])
            hist.GetXaxis().SetRangeUser(self.canvasParam[0][0],
                                            self.canvasParam[0][1])

            hist.GetXaxis().CenterTitle(True)
            hist.GetYaxis().CenterTitle(True)
            hist.SetLineWidth(2)

            # if ("_mc_" in hist.GetName()):
            #     nbins = hist.GetNbinsX()
            #     xmin  = hist.GetXaxis().GetXmin()
            #     xmax  = hist.GetXaxis().GetXmax()
            #     nominalHist = ROOT.TH1D(f"{hist.GetName()}_normalized", "", nbins, xmin, xmax)


            if (self.canvasParam[1] == True):
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]} (max @ {round(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 3)})")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]} (max @ {round(hist.GetBinContent(hist.GetMaximumBin()), 3)})")

            else:
                hist.GetXaxis().SetTitle(f"{self.canvasParam[2]}")
                hist.GetYaxis().SetTitle(f"{self.canvasParam[3]}")

            hist.SetStats(0)

            hist.Draw("hist E same")

            if ( self.canvasParam[4] != False):
                tempHist = self.canvasParam[4][0]
                tempHist.SetDirectory(0)

                tempPurHist = self.canvasParam[4][1]
                tempPurHist.SetDirectory(0)
                hLine = ROOT.TLine( self.canvasParam[0][0], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                hLine.Draw()

                vLine = ROOT.TLine( tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    self.canvasParam[0][0],
                                    tempHist.GetXaxis().GetBinCenter(tempHist.GetMaximumBin()), 
                                    tempHist.GetBinContent(tempHist.GetMaximumBin()))
                vLine.Draw()

                hLinePur = ROOT.TLine( self.canvasParam[0][0], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()),
                                    self.canvasParam[0][1], 
                                    tempPurHist.GetBinContent(tempHist.GetMaximumBin()))
                hLinePur.Draw()

                #vLine = ROOT.TLine(hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), 0, hist.GetXaxis().GetBinCenter(hist.GetMaximumBin()), hist.GetBinContent(hist.GetMaximumBin()))
                #vLine.Draw()

        prelim = ROOT.TLatex(.9, .95, "NOvA Simulation")
        prelim.SetTextColor(921)
        prelim.SetNDC()
        prelim.SetTextSize(2 / 30.)
        prelim.SetTextAlign(32)
        prelim.Draw()

        l = ROOT.TLegend(leg[0], leg[1], leg[2], leg[3])
        l.SetBorderSize(0)
        for hist,legName in zip(self.hists, leg[4]):
            l.AddEntry(hist, legName, "l")

        l.Draw()
        
        c.SaveAs(f"{self.canvasParam[6]}Ratio.pdf")
        c.SaveAs(f"{self.canvasParam[6]}Ratio.root")


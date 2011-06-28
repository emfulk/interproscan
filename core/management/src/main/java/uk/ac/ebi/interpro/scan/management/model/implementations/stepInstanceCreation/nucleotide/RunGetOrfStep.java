package uk.ac.ebi.interpro.scan.management.model.implementations.stepInstanceCreation.nucleotide;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Required;
import uk.ac.ebi.interpro.scan.management.model.StepInstance;
import uk.ac.ebi.interpro.scan.management.model.implementations.RunBinaryStep;

import java.util.ArrayList;
import java.util.List;

/**
 * @author Phil Jones
 *         Date: 21/06/11
 *         Time: 12:01
 */
public class RunGetOrfStep extends RunBinaryStep {

    private static final Logger LOGGER = Logger.getLogger(RunGetOrfStep.class.getName());

    private String fullPathToBinary;

    /**
     * The path / file name for the OUTPUT FILE (protein sequence fasta file).
     */
    private String fastaFilePath;

    public static final String SEQUENCE_FILE_PATH_KEY = "nucleic.seq.file.path";

    /**
     * Path to getorf binary.
     *
     * @param fullPathToBinary
     */
    @Required
    public void setFullPathToBinary(String fullPathToBinary) {
        this.fullPathToBinary = fullPathToBinary;
    }

    /**
     * Note this is the path template for the OUTPUT FILE - e.g. the protein sequence
     * file generated by GetOrf.
     *
     * @param fastaFilePath being the name of the protein sequence output file.
     */
    @Required
    public void setFastaFilePath(String fastaFilePath) {
        this.fastaFilePath = fastaFilePath;
    }

    @Override
    protected List<String> createCommand(StepInstance stepInstance, String temporaryFileDirectory) {
        final String nucleicAcidSeqFilePath = stepInstance.getParameters().get(SEQUENCE_FILE_PATH_KEY);
        final String fastaFile = stepInstance.buildFullyQualifiedFilePath(temporaryFileDirectory, fastaFilePath);
        final List<String> command = new ArrayList<String>();
        command.add(fullPathToBinary);
        command.add("-sequence");
        command.add(nucleicAcidSeqFilePath);
        command.add("-outseq");
        command.add(fastaFile);

        // Need to build binary switches.
        // Need to have default minimum length (100?)
        command.addAll(getBinarySwitchesAsList());
        return command;
    }
}

package uk.ac.ebi.interpro.scan.persistence;

import org.springframework.transaction.annotation.Transactional;
import uk.ac.ebi.interpro.scan.model.BlastProDomMatch;
import uk.ac.ebi.interpro.scan.model.Protein;
import uk.ac.ebi.interpro.scan.model.Signature;
import uk.ac.ebi.interpro.scan.model.SignatureLibrary;
import uk.ac.ebi.interpro.scan.model.raw.ProDomRawMatch;
import uk.ac.ebi.interpro.scan.model.raw.RawProtein;

import org.apache.commons.lang3.SerializationUtils;
import uk.ac.ebi.interpro.scan.util.Utilities;

import java.util.Collection;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * ProDom CRUD database operations.
 *
 * @author Matthew Fraser, EMBL-EBI, InterPro
 * @author Gift Nuka
 * @version $Id$
 * @since 1.0-SNAPSHOT
 */
public class ProDomFilteredMatchKVDAOImpl extends FilteredMatchKVDAOImpl<BlastProDomMatch, ProDomRawMatch>
        implements FilteredMatchKVDAO<BlastProDomMatch, ProDomRawMatch> {

    private final String proDomReleaseVersion;

    /**
     * Sets the class of the model that the DAO instance handles.
     * Note that this has been set up to use constructor injection
     * because it makes it easy to sub-class GenericDAOImpl in a robust
     * manner.
     * <p/>
     * Model class specific sub-classes should define a no-argument constructor
     * that calls this constructor with the appropriate class.
     */
    public ProDomFilteredMatchKVDAOImpl(String version) {
        super(BlastProDomMatch.class);
        this.proDomReleaseVersion = version;
    }

    /**
     * This is the method that should be implemented by specific FilteredMatchDAOImpl's to
     * persist filtered matches.
     *
     * @param filteredProteins      being the Collection of filtered RawProtein objects to persist
     * @param modelIdToSignatureMap a Map of model IDs to Signature objects.
     * @param proteinIdToProteinMap a Map of Protein IDs to Protein objects
     */
    @Transactional
    public void persist(Collection<RawProtein<ProDomRawMatch>> filteredProteins, Map<String, Signature> modelIdToSignatureMap, Map<String, Protein> proteinIdToProteinMap) {
        for (RawProtein<ProDomRawMatch> rawProtein : filteredProteins) {
            Protein protein = proteinIdToProteinMap.get(rawProtein.getProteinIdentifier());
            if (protein == null) {
                throw new IllegalStateException("Cannot store match to a protein that is not in database " +
                        "[protein ID= " + rawProtein.getProteinIdentifier() + "]");
            }
            Set<BlastProDomMatch.BlastProDomLocation> locations = null;
            String currentModelId = null;
            Signature currentSignature = null;
            ProDomRawMatch lastRawMatch = null;
            BlastProDomMatch match = null;
            HashSet<BlastProDomMatch> proteinMatches = new HashSet<>();
            for (ProDomRawMatch rawMatch : rawProtein.getMatches()) {
                if (rawMatch == null) {
                    continue;
                }

                if (currentModelId == null || !currentModelId.equals(rawMatch.getModelId())) {
                    if (currentModelId != null) {

                        // Not the first (because the currentSignatureAc is not null)
                        if (match != null) {
                            // TODO CHECK if actually not needed witht the KV store,
                            //entityManager.persist(match); // Persist the previous one...
                            //
                        }
                        match = new BlastProDomMatch(currentSignature, locations);
                        // Not the first...
                        proteinMatches.add(match);
                    }
                    // Reset everything
                    locations = new HashSet<BlastProDomMatch.BlastProDomLocation>();
                    currentModelId = rawMatch.getModelId();
                    currentSignature = modelIdToSignatureMap.get(currentModelId);
                    if (currentSignature == null) {
                        throw new IllegalStateException("Cannot find ProDom model " + currentModelId + " in the database.");
                    }
                }
                locations.add(
                        new BlastProDomMatch.BlastProDomLocation(
                                rawMatch.getLocationStart(),
                                rawMatch.getLocationEnd(),
                                rawMatch.getScore(),
                                rawMatch.getEvalue()
                        )
                );
                lastRawMatch = rawMatch;
            }

            // Don't forget the last one!
            if (lastRawMatch != null) {
                match = new BlastProDomMatch(currentSignature, locations);
                proteinMatches.add(match);
            }
            String key = Long.toString(protein.getId()) + SignatureLibrary.PRODOM.getName();
            byte[] byteKey = SerializationUtils.serialize(key);
            byte[] byteMatch = SerializationUtils.serialize(proteinMatches);
            persist(byteKey, byteMatch);
        }
        if (filteredProteins.size() > 0){
            Utilities.verboseLog("signature library : " + SignatureLibrary.PRODOM.getName());
            addSignatureLibraryName(SignatureLibrary.PRODOM.getName());
        }

    }
}
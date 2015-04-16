package edu.uw.nlp.linearization;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class TestNoPosLinearizer {

	private Linearizer linearizer;

	@Before
	public void setUp() {
		linearizer = LinearizerFactory.createLinearizer("nopos");
	}

	@Test
	public void testOutOfBounds1() {
		final String raw = "he cleared the sand and drew the following figure : l l < -LSB- -RSB- > / \\\\ `` that 's not henry the eight , '' he explained , `` but he will be in a minute .";
		final String parsed = "(S (S (NP (PRP he)) (VP (VP (VBD cleared) (NP (DT the) (NN sand))) (CC and) (VP (VBD drew) (S (NP (DT the) (VBG following)) (VP (NN figure) (: :) (S (NP-TMP (JJ l) (NN l)) (VP (VBG <) (NP (NP (NNP -LSB-) (NNP -RSB-) (NNP >) (NNP /) (NNP \\\\)) (`` ``) (SBAR (WHNP (WDT that)) (S (VP (VBZ 's) (RB not) (ADVP (RB henry)) (NP (DT the) (CD eight))))))))))))) (PRN (, ,) ('' '') (S (NP (PRP he)) (VP (VBD explained))) (, ,)) (`` ``) (CC but) (S (NP (PRP he)) (VP (MD will) (VP (VB be) (PP (IN in) (NP (DT a) (NN minute)))))) (. .))";
		final String linearized = linearizer.linearize(raw, parsed);
		Assert.assertNotNull(linearized);
	}
}

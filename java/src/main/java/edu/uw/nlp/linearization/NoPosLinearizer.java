package edu.uw.nlp.linearization;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Contains words but without their POS. Example, a tree that has S -> NP ->
 * NNP-> Dogs would become S -> NP -> Dogs
 */
public class NoPosLinearizer extends BasicLinearizer {

	@Override
	protected List<String> getPatternsPerSentence(final String rawSentence) {
		final List<String> patterns = new ArrayList<>();
		for (String terminal : rawSentence.split(" ")) {
			terminal = Pattern.quote(terminal);
			patterns.add("\\([^\\p{Z}\\p{C}]+\\s(" + terminal + ")\\)");
		}
		return patterns;
	}
}

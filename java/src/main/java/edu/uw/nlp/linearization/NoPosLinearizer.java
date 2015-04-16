package edu.uw.nlp.linearization;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Contains words but without their POS. Example, a tree that has S -> NP ->
 * NNP-> Dogs would become S -> NP -> Dogs
 */
public class NoPosLinearizer extends Linearizer {

	@Override
	public String linearize(final String rawInput, final String parsedInput) {
		final List<String> patternsStr = getPatternsPerSentence(rawInput);
		final List<Pattern> patterns = new ArrayList<>();
		for (final String patt : patternsStr) {
			patterns.add(Pattern.compile(patt));
		}
		int matches = 0;
		String result = parsedInput;
		for (final Pattern p : patterns) {
			final Matcher matcher = p.matcher(result);
			if (matcher.find()) {
				result = matcher.replaceFirst(matcher.group(1));
				matches++;
			}
		}
		assert matches == patterns.size();
		return postProcess(result);
	}

	private static List<String> getPatternsPerSentence(final String rawSentence) {
		final List<String> patterns = new ArrayList<>();
		for (String terminal : rawSentence.split(" ")) {
			if (terminal.contains("*") || terminal.contains("+")) {
				terminal = terminal.replaceAll("\\*", "\\\\*");
				terminal = terminal.replaceAll("\\+", "\\\\+");
			}

			patterns.add("\\([^\\p{Z}\\p{C}]+\\s(" + terminal + ")\\)");
		}
		return patterns;
	}
}

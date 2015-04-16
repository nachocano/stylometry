package edu.uw.nlp.linearization;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.uw.nlp.utils.Utils;

public abstract class Linearizer {

	public String linearize(final String rawInput, final String parsedInput) {
		final String newRawInput = Utils.cleanup(rawInput);
		final List<String> patternsStr = getPatternsPerSentence(newRawInput);
		final List<Pattern> patterns = new ArrayList<>();
		for (final String patt : patternsStr) {
			patterns.add(Pattern.compile(patt));
		}
		int matches = 0;
		String result = Utils.cleanup(parsedInput);
		for (final Pattern p : patterns) {
			final Matcher matcher = p.matcher(result);
			if (matcher.find()) {
				result = matcher.replaceAll(matcher.group(1));
				matches++;
			}
		}
		assert matches == patterns.size();
		return postProcess(result);
	}

	protected abstract List<String> getPatternsPerSentence(String rawSentence);

	public String postProcess(final String linearized) {
		final StringBuilder sb = new StringBuilder();
		final Stack<String> stack = new Stack<>();
		final char[] array = linearized.toCharArray();
		for (int i = 0; i < array.length; i++) {
			if (array[i] == '(') {
				final StringBuilder sStack = new StringBuilder();
				int j = i + 1;
				while (array[j] != ' ') {
					sStack.append(array[j]);
					j++;
				}
				stack.add(sStack.toString());
				sb.append("(");
			} else if (array[i] == ')') {
				sb.append(" )" + stack.pop());
			} else {
				sb.append(array[i]);
			}
		}
		return sb.toString();
	}
}

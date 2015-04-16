package edu.uw.nlp.linearization;

import java.util.Stack;

public abstract class Linearizer {

	public abstract String linearize(String rawInput, String parsedInput);

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

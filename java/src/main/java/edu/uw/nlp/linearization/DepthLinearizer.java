package edu.uw.nlp.linearization;

import org.apache.commons.lang3.Validate;

public class DepthLinearizer implements Linearizer {

	private int depth;
	private boolean verticalMarkovization = false;
	private static final String WHITESPACE = " ";

	@Override
	public void init(final String param) {
		Validate.notBlank(param);
		final String[] ps = param.split(",");
		this.depth = Integer.valueOf(ps[0]);
		if (ps.length > 1) {
			this.verticalMarkovization = Boolean.valueOf(ps[1]);
		}
	}

	@Override
	public String linearize(final String rawInput, final String parsedInput) {
		String result = "";
		int tempDepth = depth;
		// remove root from parsed input
		String parsed = parsedInput;
		if (parsedInput.startsWith("(ROOT ")) {
			parsed = parsedInput.replaceFirst("\\(ROOT ", "");
			parsed = parsed.substring(0, parsed.length() - 1);
		}
		while (tempDepth >= 2) {
			final StringBuilder sb = new StringBuilder();
			int count = 0;
			boolean possibleMark = false;
			final char[] array = parsed.toCharArray();
			for (int i = 0; i < array.length; i++) {
				if (array[i] == '(') {
					count++;
					if (count == tempDepth) {
						final StringBuilder partial = new StringBuilder();
						int j = i + 1;
						while (array[j] != ' ') {
							partial.append(array[j]);
							j++;
						}
						sb.append(partial.toString()).append(WHITESPACE);
						possibleMark = true;
					} else if (verticalMarkovization && count == tempDepth + 1
							&& possibleMark) {
						final StringBuilder partial = new StringBuilder();
						int j = i + 1;
						while (array[j] != ' ') {
							partial.append(array[j]);
							j++;
						}
						final String possibleMarkovization = partial.toString();
						if (!rawInput.contains(possibleMarkovization)) {
							// markovize (remove previous space and add new one)
							sb.delete(sb.length() - 1, sb.length());
							sb.append("^" + partial.toString()).append(
									WHITESPACE);
						}
						possibleMark = false;
					}
				} else if (array[i] == ')') {
					count--;
					Validate.isTrue(count >= 0);
				} else {
					// do nothing
				}
			}
			if (sb.length() == 0) {
				tempDepth--;
			} else {
				result = sb.substring(0, sb.length() - 1);
				break;
			}
		}
		// System.out.println(result);
		return result;
	}

}

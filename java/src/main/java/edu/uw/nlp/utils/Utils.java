package edu.uw.nlp.utils;

import org.apache.commons.lang3.StringEscapeUtils;
import org.apache.commons.lang3.StringUtils;

public class Utils {

	private Utils() {
	}

	public static String replace(final String str, final String exp,
			final String replacement) {
		return StringUtils.replace(str, exp, replacement);
	}

	public static String replaceDollarSign(final String str) {
		return replace(str, "$", "DOLLAR_SIGN");
	}

	public static String replaceDoubleQuotes(final String str) {
		final String str1 = replace(str, "``", "DOUBLE_QUOTES");
		return replace(str1, "''", "DOUBLE_QUOTES");
	}

	public static String escapeHtml(final String str) {
		return StringEscapeUtils.escapeHtml4(str);
	}

	public static String replaceBar(final String str) {
		return replace(str, "\\", "BAR");
	}

	public static String cleanup(final String str) {
		final String str1 = replaceDollarSign(str);
		final String str2 = replaceBar(str1);
		return str2;
	}

}

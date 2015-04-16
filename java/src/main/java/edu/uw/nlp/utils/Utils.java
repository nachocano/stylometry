package edu.uw.nlp.utils;

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

}

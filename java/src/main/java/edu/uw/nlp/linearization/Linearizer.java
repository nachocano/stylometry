package edu.uw.nlp.linearization;

public interface Linearizer {

	void init(final String params);

	String linearize(final String rawInput, final String parsedInput);

}

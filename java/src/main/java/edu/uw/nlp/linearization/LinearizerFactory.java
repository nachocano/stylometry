package edu.uw.nlp.linearization;

public class LinearizerFactory {

	private static final String NO_POS = "nopos";
	private static final String NO_WORDS = "nowords";
	private static final String DEPTH = "depth";

	private LinearizerFactory() {
	}

	public static Linearizer createLinearizer(final String name) {
		if (NO_POS.equals(name)) {
			return new NoPosLinearizer();
		} else if (NO_WORDS.equals(name)) {
			return new NoWordsLinearizer();
		} else if (DEPTH.equals(name)) {
			return new DepthLinearizer();
		} else {
			throw new RuntimeException("Invalid linearizer");
		}

	}
}

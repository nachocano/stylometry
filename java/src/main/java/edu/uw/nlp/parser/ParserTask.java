package edu.uw.nlp.parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;

import org.apache.commons.lang3.Validate;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Word;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreebankLanguagePack;

public class ParserTask implements Callable<Void> {

	private final File output;
	private final String name;
	private final File input;
	private final LexicalizedParser lp;
	private final TreebankLanguagePack tlp;

	public ParserTask(final LexicalizedParser lp,
			final TreebankLanguagePack tlp, final File inputDoc,
			final File outputFolder) {
		Validate.notNull(inputDoc);
		Validate.notNull(outputFolder);
		Validate.notNull(lp);
		this.name = inputDoc.getName();
		this.output = new File(outputFolder, inputDoc.getName() + ".pcfg");
		this.input = inputDoc;
		this.lp = lp;
		this.tlp = tlp;
	}

	@Override
	public Void call() throws Exception {
		final long start = System.currentTimeMillis();
		System.out.println("processing " + output.toString());
		PrintWriter pw = null;
		BufferedReader reader = null;
		try {
			pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(
					output), "utf-8"));
			reader = new BufferedReader(new InputStreamReader(
					new FileInputStream(input), "utf-8"));

			final List<List<HasWord>> sentences = new ArrayList<>();
			String line = null;
			while ((line = reader.readLine()) != null) {
				final String[] strs = line.split(" ");
				if (strs != null && strs.length > 1) {
					final List<HasWord> sentenceAsWord = new ArrayList<>();
					for (final String str : strs) {
						sentenceAsWord.add(new Word(str));
					}
					sentences.add(sentenceAsWord);
				}
			}
			for (final List<HasWord> sentence : sentences) {
				final Tree tree = lp.parse(sentence).skipRoot();
				pw.println(tree);
			}

			// final DocumentPreprocessor documentPreprocessor = new
			// DocumentPreprocessor(
			// reader);
			// documentPreprocessor.setTokenizerFactory(tlp.getTokenizerFactory());
			// for (final List<HasWord> sentence : documentPreprocessor) {
			// final Tree tree = lp.parse(sentence).skipRoot();
			// pw.println(tree);
			// }
		} catch (final Exception exc) {
			System.out.println(String.format("%s exception: %s", name,
					exc.getMessage()));
		} finally {
			if (reader != null) {
				reader.close();
			}
			if (pw != null) {
				pw.close();
			}
			System.out.println(String.format("processed %s in %s",
					output.toString(),
					(System.currentTimeMillis() - start) / 1000));
		}
		return null;
	}
}

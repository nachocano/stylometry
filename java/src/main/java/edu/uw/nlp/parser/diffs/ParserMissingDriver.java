package edu.uw.nlp.parser.diffs;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.uw.nlp.concurrent.Utils;
import edu.uw.nlp.parser.ParserTask;

public class ParserMissingDriver {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i", true, "input file");

		final CommandLineParser parser = new BasicParser();

		String inputFile = null;

		try {
			final CommandLine line = parser.parse(options, args);
			inputFile = line.getOptionValue("i");
			Validate.notNull(inputFile);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("parsermissing", options);
			throw e;
		}

		final String grammar = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
		final String[] opt = { "-maxLength", "80", "-retainTmpSubcategories" };
		final LexicalizedParser lp = LexicalizedParser.loadModel(grammar, opt);
		final TreebankLanguagePack tlp = lp.getOp().langpack();

		final List<ParserTask> tasks = new ArrayList<>();

		BufferedReader reader = null;

		try {

			reader = new BufferedReader(new InputStreamReader(
					new FileInputStream(inputFile), "utf-8"));
			String line = null;
			while ((line = reader.readLine()) != null) {
				final String[] filenames = line.split("\t");
				Validate.isTrue(filenames.length == 2);
				final ParserTask pt = new ParserTask(lp, tlp, filenames[0],
						filenames[1]);
				tasks.add(pt);
			}

		} catch (final Exception exc) {
			System.out
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (reader != null) {
				reader.close();
			}
		}

		final long start = System.currentTimeMillis();

		Utils.parallelExecute(tasks);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));

	}
}

package edu.uw.nlp.parser;

import java.io.File;
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

/**
 * Parse Novels with Stanford Parser
 */
public class ParserDriver {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i", true, "input folder");
		options.addOption("o", true, "output folder");

		final CommandLineParser parser = new BasicParser();

		String inputFolder = null;
		String outputFolder = null;

		try {
			final CommandLine line = parser.parse(options, args);
			inputFolder = line.getOptionValue("i");
			Validate.notNull(inputFolder);
			outputFolder = line.getOptionValue("o");
			Validate.notNull(outputFolder);
		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("parser", options);
			throw e;
		}

		final String grammar = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
		final String[] opt = { "-maxLength", "80", "-retainTmpSubcategories" };
		final LexicalizedParser lp = LexicalizedParser.loadModel(grammar, opt);
		final TreebankLanguagePack tlp = lp.getOp().langpack();

		final List<ParserTask> tasks = new ArrayList<>();

		System.out.println("creating folders and files...");
		final File inputF = new File(inputFolder);
		final File outputF = new File(outputFolder);
		if (!outputF.exists()) {
			outputF.mkdir();
		}
		// for (final File genreFolder : inputF.listFiles()) {
		// if (genreFolder.isFile()) {
		// continue;
		// }
		System.out.println("genre folder: " + inputF.getName());
		final File genreOutputF = new File(outputF, inputF.getName());
		genreOutputF.mkdir();
		for (final File foldFolder : inputF.listFiles()) {
			if (foldFolder.isFile()) {
				continue;
			}
			System.out.println(" fold folder: " + foldFolder.getName());
			final File foldOutputF = new File(genreOutputF,
					foldFolder.getName());
			foldOutputF.mkdir();
			for (final File failSuccessFolder : foldFolder.listFiles()) {
				if (failSuccessFolder.isFile()) {
					continue;
				}
				System.out.println("  fail Success folder: "
						+ failSuccessFolder.getName());
				final File failSuccessOutputF = new File(foldOutputF,
						failSuccessFolder.getName());
				failSuccessOutputF.mkdir();
				for (final File document : failSuccessFolder.listFiles()) {
					if (document.isDirectory()
							|| document.getName().startsWith(".")) {
						continue;
					}
					System.out.println("   document: " + document.getName());
					final ParserTask pt = new ParserTask(lp, tlp, document,
							failSuccessOutputF);
					tasks.add(pt);
				}
			}
		}
		// }
		System.out.println("created folders and files. processing...");
		final long start = System.currentTimeMillis();

		Utils.parallelExecute(tasks);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

}

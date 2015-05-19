package edu.uw.nlp.linearization;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

public class LinearizationDriverNovels {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i1", true, "raw sent folder");
		options.addOption("i2", true, "parsed folder");
		options.addOption("o", true, "linearized folder");
		options.addOption("l", true, "linearizer");
		options.addOption("p", true, "params");

		final CommandLineParser parser = new BasicParser();

		String input1Folder = null;
		String input2Folder = null;
		String outputFolder = null;
		String linearizerName = null;
		String params = null;

		try {
			final CommandLine line = parser.parse(options, args);
			input1Folder = line.getOptionValue("i1");
			Validate.notNull(input1Folder);
			input2Folder = line.getOptionValue("i2");
			Validate.notNull(input2Folder);
			outputFolder = line.getOptionValue("o");
			Validate.notNull(outputFolder);
			linearizerName = line.getOptionValue("l");
			Validate.notNull(linearizerName);
			params = line.getOptionValue("p");
		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("parser", options);
			throw e;
		}

		final long start = System.currentTimeMillis();
		System.out.println("processing folders and files...");
		final File input1F = new File(input1Folder);
		final File input2F = new File(input2Folder);
		final File outputF = new File(outputFolder);

		final Linearizer linearizer = LinearizerFactory
				.createLinearizer(linearizerName);
		linearizer.init(params);

		if (!outputF.exists()) {
			outputF.mkdir();
		}
		for (final File genreFolder : input1F.listFiles()) {
			if (genreFolder.isFile()) {
				continue;
			}
			System.out.println("genre folder: " + genreFolder.getName());
			final File genreInput2F = new File(input2F, genreFolder.getName());
			final File genreOutputF = new File(outputF, genreFolder.getName());
			genreOutputF.mkdir();
			for (final File foldFolder : genreFolder.listFiles()) {
				if (foldFolder.isFile()) {
					continue;
				}
				System.out.println(" fold folder: " + foldFolder.getName());
				final File foldInput2F = new File(genreInput2F,
						foldFolder.getName());
				final File foldOutputF = new File(genreOutputF,
						foldFolder.getName());
				foldOutputF.mkdir();
				for (final File failSuccessFolder : foldFolder.listFiles()) {
					if (failSuccessFolder.isFile()) {
						continue;
					}
					System.out.println("  fail Success folder: "
							+ failSuccessFolder.getName());
					final File failSuccessInput2F = new File(foldInput2F,
							failSuccessFolder.getName());
					final File failSuccessOutputF = new File(foldOutputF,
							failSuccessFolder.getName());
					failSuccessOutputF.mkdir();
					for (final File document : failSuccessFolder.listFiles()) {
						if (document.isDirectory()
								|| document.getName().startsWith(".")) {
							continue;
						}
						System.out
								.println("   document: " + document.getName());
						final File parsedDoc = new File(failSuccessInput2F,
								document.getName() + ".pcfg");
						final File linearizedDoc = new File(failSuccessOutputF,
								document.getName() + ".lpcfg");
						PrintWriter pw = null;
						BufferedReader readerRaw = null;
						BufferedReader readerParsed = null;
						try {
							pw = new PrintWriter(new OutputStreamWriter(
									new FileOutputStream(linearizedDoc),
									"utf-8"));
							readerRaw = new BufferedReader(
									new InputStreamReader(new FileInputStream(
											document), "utf-8"));
							readerParsed = new BufferedReader(
									new InputStreamReader(new FileInputStream(
											parsedDoc), "utf-8"));
							String rawSentence, parsedSentence = null;
							while ((rawSentence = readerRaw.readLine()) != null
									&& (parsedSentence = readerParsed
											.readLine()) != null) {
								final String linearized = linearizer.linearize(
										rawSentence, parsedSentence);
								pw.println(linearized);
							}

						} catch (final Exception exc) {
							System.out.println(String.format("exception: %s",
									exc.getMessage()));
							return;
						} finally {
							if (readerRaw != null) {
								readerRaw.close();
							}
							if (readerParsed != null) {
								readerParsed.close();
							}
							if (pw != null) {
								pw.close();
							}

						}
					}
				}
			}
		}
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

}

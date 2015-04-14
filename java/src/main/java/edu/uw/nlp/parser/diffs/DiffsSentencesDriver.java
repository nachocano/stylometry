package edu.uw.nlp.parser.diffs;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

public class DiffsSentencesDriver {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i", true, "raw folder");
		options.addOption("o", true, "parsed folder");
		options.addOption("f", true, "output file");

		final CommandLineParser parser = new BasicParser();

		String inputFolder = null;
		String outputFolder = null;
		String outputFile = null;

		try {
			final CommandLine line = parser.parse(options, args);
			inputFolder = line.getOptionValue("i");
			Validate.notNull(inputFolder);
			outputFolder = line.getOptionValue("o");
			Validate.notNull(outputFolder);
			outputFile = line.getOptionValue("f");
			Validate.notNull(outputFile);
		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("diffs", options);
			throw e;
		}

		final Map<FileKey, Integer> raws = new HashMap<>();
		final Map<FileKey, Integer> parsed = new HashMap<>();
		final File genreInputF = new File(inputFolder);
		final File genreOutputF = new File(outputFolder);

		final PrintWriter pw = new PrintWriter(new OutputStreamWriter(
				new FileOutputStream(outputFile), "utf-8"));

		System.out.println("genre folder: " + genreInputF.getName());
		for (final File foldFolder : genreInputF.listFiles()) {
			if (foldFolder.isFile()) {
				continue;
			}
			System.out.println(" fold folder: " + foldFolder.getName());
			final File foldOutputF = new File(genreOutputF,
					foldFolder.getName());

			for (final File failSuccessFolder : foldFolder.listFiles()) {
				if (failSuccessFolder.isFile()) {
					continue;
				}
				System.out.println("  fail Success folder: "
						+ failSuccessFolder.getName());

				final File failSuccessOutputF = new File(foldOutputF,
						failSuccessFolder.getName());

				for (final File document : failSuccessFolder.listFiles()) {
					if (document.isDirectory()
							|| document.getName().startsWith(".")) {
						continue;
					}
					System.out.println("   document: " + document.getName());
					raws.put(
							new FileKey(document.getName(), document.getPath()),
							getLineNumbers(document));
					final File parsedDocument = new File(failSuccessOutputF,
							document.getName() + ".pcfg");
					if (!parsedDocument.exists()) {
						pw.println(document.toString());
					} else {
						parsed.put(
								new FileKey(parsedDocument.getName().replace(
										".pcfg", ""), parsedDocument.getPath()),
								getLineNumbers(parsedDocument));
					}
				}
			}
		}

		for (final FileKey key : parsed.keySet()) {
			final Integer rawCount = raws.get(key);
			final Integer parsedCount = parsed.get(key);
			if (rawCount != parsedCount) {
				// ugly stuff
				for (final FileKey rKey : raws.keySet()) {
					if (rKey.equals(key)) {
						System.out.println(String.format(
								"file: %s, rawCount: %s, parsedCount: %s",
								rKey.path, rawCount, parsedCount));
						pw.println(rKey.path);
						break;
					}
				}
			}
		}

		pw.close();

	}

	private static Integer getLineNumbers(final File document) {
		BufferedReader reader = null;
		int counter = 0;
		try {
			reader = new BufferedReader(new InputStreamReader(
					new FileInputStream(document), "utf-8"));
			while (reader.readLine() != null) {
				counter += 1;
			}
		} catch (final Exception e) {
			System.out.println("exception: " + e.getMessage());
		} finally {
			if (reader != null) {
				try {
					reader.close();
				} catch (final IOException e) {
					// nothing here
				}
			}
		}
		return counter;
	}

	private static final class FileKey {
		String filename;
		String path;

		FileKey(final String filename, final String path) {
			this.filename = filename;
			this.path = path;
		}

		@Override
		public int hashCode() {
			final int prime = 31;
			int result = 1;
			result = prime * result
					+ (filename == null ? 0 : filename.hashCode());
			return result;
		}

		@Override
		public boolean equals(final Object obj) {
			if (this == obj) {
				return true;
			}
			if (obj == null) {
				return false;
			}
			if (getClass() != obj.getClass()) {
				return false;
			}
			final FileKey other = (FileKey) obj;
			if (filename == null) {
				if (other.filename != null) {
					return false;
				}
			} else if (!filename.equals(other.filename)) {
				return false;
			}
			return true;
		}

	}
}

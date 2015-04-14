package edu.uw.nlp.concurrent;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import edu.uw.nlp.parser.ParserTask;

public class Utils {

	private Utils() {

	}

	public static void parallelExecute(final List<ParserTask> tasks) {
		final ExecutorService executor = Executors.newFixedThreadPool(2);
		try {
			final List<Future<Void>> futures = executor.invokeAll(tasks);
			for (final Future<Void> f : futures) {
				f.get();
			}
		} catch (final InterruptedException e) {
			System.out.println(String.format(
					"error: interrupted exception: %s", e.getMessage()));
		} catch (final Exception e) {
			System.out.println(String.format("error: exception: %s",
					e.getMessage()));
		} finally {
			executor.shutdown();
		}
	}

}

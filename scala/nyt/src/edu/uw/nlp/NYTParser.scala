package edu.uw.nlp

import java.io.{FileOutputStream, OutputStreamWriter, PrintWriter, File}

import nlp_serde.readers.PerLineJsonReader

import scala.collection.mutable.ArrayBuffer

object NYTParser {

  def main(args: Array[String]) {
    if (args.length != 6) {
      println("arg1:great\narg2:verygood\narg3:typical\narg4:inputDir\narg5:outputTextDir\narg6:outputParseDir")
      System.exit(1)
    }

    val great : ArrayBuffer[String] = Utils.readLines(args(0))
    val veryGood : ArrayBuffer[String] = Utils.readLines(args(1))
    val typical : ArrayBuffer[String] = Utils.readLines(args(2))

    println("great size " + great.size)
    println("very good size " + veryGood.size)
    println("typical size " + typical.size)

    val map = new scala.collection.mutable.HashMap[String, String]()
    Utils.addToMap(map, great, "great")
    Utils.addToMap(map, veryGood, "verygood")
    Utils.addToMap(map, typical, "typical")

    val outputTextDir : File = new File(args(4))
    if (!outputTextDir.exists()) {
      outputTextDir.mkdir()
    }
    val outputParseDir : File = new File(args(5))
    if (!outputParseDir.exists()) {
      outputParseDir.mkdir()
    }
    var count : Int = 0
    val inputFiles = new File(args(3)).listFiles()
    for (file <- inputFiles) {
      for (d <- new PerLineJsonReader(true).read(file.getAbsolutePath)) {
        if (d.path.get != null) {
          if (map.contains(d.path.get)) {
            count += 1
            val newFileName = d.path.get.replaceAll("/", "_")
            val textDir = new File(outputTextDir, map(d.path.get))
            if (!textDir.exists()) {
              textDir.mkdir()
            }
            val parseDir = new File(outputParseDir, map(d.path.get))
            if (!parseDir.exists()) {
              parseDir.mkdir()
            }
            val textFile = new PrintWriter(new OutputStreamWriter(new FileOutputStream(
              new File(textDir, newFileName)), "utf-8"))
            val parsedFile = new PrintWriter(new OutputStreamWriter(new FileOutputStream(
              new File(parseDir, newFileName + ".pcfg")), "utf-8"))
            for (s <- d.sentences) {
              textFile.println(s.text)
              parsedFile.println(s.parseTree.get)
            }
            textFile.close()
            parsedFile.close()
          } else {
            println(d.path.get + " not in the list")
          }
        }
      }
    }
    println("map size: " + map.size + ", count size: " + count)
  }

}

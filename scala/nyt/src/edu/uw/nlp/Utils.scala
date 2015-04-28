package edu.uw.nlp

import java.io.File

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

object Utils {


  def readLines(filename: String): ArrayBuffer[String] = {
    val lines: ArrayBuffer[String] = new ArrayBuffer[String]
    val file = new File(filename)
    for (line <- Source.fromFile(file).getLines) {
      lines += line.replaceAll("_","/")
    }
    lines
  }


  def addToMap(map : scala.collection.mutable.Map[String, String], arr: ArrayBuffer[String], value : String) : Unit = {
    for (elem <- arr) {
      map += elem -> value
    }
  }

}

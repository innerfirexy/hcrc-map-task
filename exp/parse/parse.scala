// Parse `tokens` column of utterances table of map db
// Yang Xu
// 2/10/2016

import java.sql.{Connection, DriverManager, ResultSet}

import epic.preprocess
import epic.models.{NerSelector, ParserSelector}


object Parse {
    def main(args: Array[String]): Unit = {
        val conn_str = "jdbc:mysql://localhost:1234/map?user=yang&password=05012014"
        Class.forName("com.mysql.jdbc.Driver")
        val conn = DriverManager.getConnection(conn_str)

        val tokenizer = new epic.preprocess.TreebankTokenizer()
        val parser = ParserSelector.loadParser("en").get

        try {
            val statement = conn.createStatement(ResultSet.TYPE_FORWARD_ONLY, ResultSet.CONCUR_READ_ONLY)
            val rs = statement.executeQuery("SELECT tokens FROM utterances LIMIT 5")
            while (rs.next) {
                val sent = rs.getString("tokens")
                println(sent)
                //tokenize
                val tokens = tokenizer(sent).toIndexedSeq
                //parse
                val tree = parser(tokens)
                println(tree.render(tokens))
            }
        } catch {
          case e: Exception => e.printStackTrace
        } finally {
            conn.close()
        }
    }
}

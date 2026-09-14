import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    // 이 기사에 연결된 유튜브 영상 주소 (나중에는 API 응답값으로 대체됨)
    private val newsVideoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnYoutubeLink = findViewById<Button>(R.id.btnYoutubeLink)
        btnYoutubeLink.setOnClickListener {
            openExternalLink(newsVideoUrl)
        }
    }

    private fun openExternalLink(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "링크를 열 수 없어요", Toast.LENGTH_SHORT).show()
        }
    }
}

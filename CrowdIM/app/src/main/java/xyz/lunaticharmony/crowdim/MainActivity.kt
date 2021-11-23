package xyz.lunaticharmony.crowdim

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Toast
import xyz.lunaticharmony.crowdim.ui.main.MainFragment

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

//    https://stackoverflow.com/questions/44301301/android-how-to-achieve-setonclicklistener-in-kotlin
    fun checkButton(view: View) {
        Toast.makeText(view.context, "your toast text", Toast.LENGTH_SHORT).show();
    }
}


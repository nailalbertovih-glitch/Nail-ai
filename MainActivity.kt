package com.nailai.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { NailAiScreen() }
    }
}

@Composable
fun NailAiScreen() {
    var enabled by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Backend не подключён") }
    MaterialTheme {
        Scaffold { padding ->
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding).padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Text("NAIL AI", style = MaterialTheme.typography.headlineLarge)
                    Text("Персональный помощник Telegram", style = MaterialTheme.typography.bodyMedium)
                }
                item {
                    Card {
                        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Состояние системы", style = MaterialTheme.typography.titleMedium)
                            Text(status)
                            Text("Автоотправка: выключена")
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Button(onClick = { enabled = !enabled; status = if (enabled) "Локальный демонстрационный режим" else "Backend не подключён" }) {
                                    Text(if (enabled) "Выключить" else "Тестовый режим")
                                }
                            }
                        }
                    }
                }
                item {
                    Text("Черновики ответов", style = MaterialTheme.typography.titleLarge)
                    Text("Здесь будут появляться варианты ответов. Отправка будет возможна только после ручного подтверждения.")
                }
                items(listOf("Подключение Telegram — ещё не настроено", "ИИ и память — ещё не настроены", "Сервер — ещё не подключён")) { line ->
                    ListItem(headlineContent = { Text(line) })
                }
                item {
                    Text("Важно: это стартовый интерфейс. Он пока не читает Telegram и не отправляет сообщения.", style = MaterialTheme.typography.bodySmall)
                }
            }
        }
    }
}

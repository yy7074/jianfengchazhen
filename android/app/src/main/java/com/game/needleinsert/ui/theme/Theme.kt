package com.game.needleinsert.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// 游戏主题色彩
object GameColors {
    val PrimaryBlue = Color(0xFF2196F3)
    val PrimaryPurple = Color(0xFF9C27B0)
    val SecondaryTeal = Color(0xFF00BCD4)
    val AccentOrange = Color(0xFFFF9800)
    val AccentPink = Color(0xFFE91E63)
    val GoldYellow = Color(0xFFFFD700)
    val EmeraldGreen = Color(0xFF4CAF50)
    val DeepPurple = Color(0xFF673AB7)
    val SkyBlue = Color(0xFF87CEEB)
    val SunsetOrange = Color(0xFFFF6B35)
    val MidnightBlue = Color(0xFF191970)
    val RoyalPurple = Color(0xFF7B68EE)
    val NeonGreen = Color(0xFF39FF14)
    val ElectricBlue = Color(0xFF7DF9FF)
    val HotPink = Color(0xFFFF1493)
    val LimeGreen = Color(0xFF32CD32)
}

private val DarkColorScheme = darkColorScheme(
    primary = GameColors.RoyalPurple,
    secondary = GameColors.SecondaryTeal,
    tertiary = GameColors.AccentPink,
    background = GameColors.MidnightBlue,
    surface = Color(0xFF1A1A2E),
    onPrimary = Color.White,
    onSecondary = Color.White,
    onTertiary = Color.White,
    onBackground = Color.White,
    onSurface = Color.White,
)

private val LightColorScheme = lightColorScheme(
    primary = GameColors.PrimaryBlue,
    secondary = GameColors.SecondaryTeal,
    tertiary = GameColors.AccentOrange,
    background = Color(0xFFF0F8FF),
    surface = Color.White,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onTertiary = Color.White,
    onBackground = Color(0xFF1A1A2E),
    onSurface = Color(0xFF1A1A2E),
)

@Composable
fun NeedleInsertTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
} 
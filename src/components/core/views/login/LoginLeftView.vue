<!-- 登录、注册、忘记密码左侧背景 -->
<template>
  <div class="login-left-view">
    <!-- 背景动态网格 -->
    <div class="grid-bg"></div>
    <div class="grid-bg grid-bg-2"></div>

    <!-- 声纳扫描波纹 -->
    <div class="sonar-ripple"></div>
    <div class="sonar-ripple delay"></div>

    <!-- 品牌 Logo -->
    <div class="logo">
      <ArtLogo class="icon" size="46" />
      <h1 class="title">{{ AppConfig.systemInfo.name }}</h1>
    </div>

    <!-- 品牌 X 标志动画 -->
    <div class="brand-x-mark">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="x-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#4A90E2" />
            <stop offset="100%" stop-color="#4CAF50" />
          </linearGradient>
        </defs>
        <path
          d="M10,50 L50,10 L90,50 L50,90 Z"
          fill="none"
          stroke="url(#x-gradient)"
          stroke-width="8"
          class="x-line"
        />
        <path
          d="M10,50 L50,10 L90,50 L50,90 Z"
          fill="none"
          stroke="url(#x-gradient)"
          stroke-width="8"
          transform="rotate(45 50 50)"
          class="x-line"
        />
      </svg>
    </div>

    <!-- 医学影像核心图标 -->
    <div class="left-img">
      <ThemeSvg :src="medicalAiIcon" size="100%" class="ai-core" />
    </div>

    <!-- 文案区域 -->
    <div class="text-wrap">
      <h1>{{ $t('login.leftView.title') }}</h1>
      <p>{{ $t('login.leftView.subTitle') }}</p>
    </div>

    <!-- 扫描光效 -->
    <div class="scan-beam"></div>
  </div>
</template>

<script setup lang="ts">
  import AppConfig from '@/config'
  import medicalAiIcon from '@imgs/svg/medical_ai_icon.svg'
</script>

<style lang="scss" scoped>
  $primary-blue: #4a90e2;
  $primary-green: #4caf50;
  $primary-purple: #5e6ad9;
  $dark-bg: #0a0f25;

  $bg-gradient: linear-gradient(
    135deg,
    color-mix(in srgb, $primary-blue 100%, #f0f6ff) 0%,
    color-mix(in srgb, $primary-purple 80%, #f0f6ff) 50%,
    color-mix(in srgb, $primary-green 60%, #f0f6ff) 100%
  );

  .login-left-view {
    position: relative;
    width: 65vw;
    height: 100%;
    padding: 15px;
    overflow: hidden;
    background: $bg-gradient;

    // 动态网格背景
    .grid-bg {
      position: absolute;
      inset: 0;
      background-image:
        repeating-linear-gradient(
          to right,
          rgba(255, 255, 255, 0.06) 0px,
          rgba(255, 255, 255, 0.06) 1px,
          transparent 1px,
          transparent 40px
        ),
        repeating-linear-gradient(
          to bottom,
          rgba(255, 255, 255, 0.06) 0px,
          rgba(255, 255, 255, 0.06) 1px,
          transparent 1px,
          transparent 40px
        );
      animation: moveGrid 20s linear infinite;
      z-index: 1;
    }

    .grid-bg-2 {
      opacity: 0.4;
      animation: moveGridReverse 25s linear infinite;
    }

    // 声纳扫描波纹
    .sonar-ripple {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      background: radial-gradient(circle, rgba(74, 144, 226, 0.25) 20%, transparent 70%);
      animation: ripple 6s linear infinite;
      z-index: 2;
      pointer-events: none;
    }

    .sonar-ripple.delay {
      animation-delay: 3s;
    }

    .logo {
      position: relative;
      z-index: 10;
      display: flex;
      align-items: center;
      margin-bottom: 40px;

      .title {
        margin-left: 10px;
        font-size: 20px;
        font-weight: 400;
        color: var(--art-text-gray-900);
      }
    }

    .brand-x-mark {
      position: absolute;
      top: 30%;
      left: 50%;
      transform: translateX(-50%);
      width: 100px;
      height: 100px;
      z-index: 5;

      .x-line {
        stroke-dasharray: 200;
        stroke-dashoffset: 200;
        animation:
          dash 6s linear infinite,
          glowPulse 3s infinite ease-in-out;
      }

      svg {
        width: 100%;
        height: 100%;
      }
    }

    .left-img {
      position: absolute;
      inset: 0 0 10.5%;
      z-index: 5;
      width: 40%;
      margin: auto;

      .ai-core {
        animation: breathe 4s infinite ease-in-out;
      }
    }

    .text-wrap {
      position: absolute;
      bottom: 80px;
      width: 100%;
      text-align: center;
      z-index: 10;

      h1 {
        font-size: 24px;
        font-weight: 500;
        color: $primary-blue;
        margin-bottom: 8px;
      }

      p {
        font-size: 14px;
        color: var(--art-text-gray-600);
      }
    }

    .scan-beam {
      position: absolute;
      top: 20%;
      left: 50%;
      width: 3px;
      height: 60%;
      background: linear-gradient(180deg, transparent, $primary-blue, transparent);
      opacity: 0.6;
      transform-origin: center;
      box-shadow: 0 0 20px rgba(74, 144, 226, 0.6);
      animation:
        scanBeam 2s infinite alternate,
        beamRotate 8s infinite ease-in-out;
      z-index: 2;
    }

    // 动画定义
    @keyframes moveGrid {
      from {
        transform: translate(0, 0);
      }
      to {
        transform: translate(40px, 40px);
      }
    }

    @keyframes moveGridReverse {
      from {
        transform: translate(0, 0);
      }
      to {
        transform: translate(-40px, -40px);
      }
    }

    @keyframes ripple {
      0% {
        width: 0;
        height: 0;
        opacity: 0.4;
      }
      70% {
        opacity: 0.15;
      }
      100% {
        width: 1200px;
        height: 1200px;
        opacity: 0;
      }
    }

    @keyframes dash {
      to {
        stroke-dashoffset: 0;
      }
    }

    @keyframes glowPulse {
      0%,
      100% {
        filter: drop-shadow(0 0 5px $primary-blue);
      }
      50% {
        filter: drop-shadow(0 0 15px $primary-green);
      }
    }

    @keyframes breathe {
      0%,
      100% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.05);
      }
    }

    @keyframes scanBeam {
      0% {
        transform: scaleY(0);
        opacity: 0;
      }
      50% {
        transform: scaleY(1);
        opacity: 0.6;
      }
      100% {
        transform: scaleY(0);
        opacity: 0;
      }
    }

    @keyframes beamRotate {
      0% {
        transform: rotate(-5deg);
      }
      50% {
        transform: rotate(5deg);
      }
      100% {
        transform: rotate(-5deg);
      }
    }
  }

  .dark .login-left-view {
    background: linear-gradient(
      135deg,
      $dark-bg 0%,
      color-mix(in srgb, $dark-bg 80%, #000) 50%,
      $dark-bg 100%
    );

    .grid-bg {
      background-image:
        repeating-linear-gradient(
          to right,
          rgba(255, 255, 255, 0.08) 0px,
          rgba(255, 255, 255, 0.08) 1px,
          transparent 1px,
          transparent 40px
        ),
        repeating-linear-gradient(
          to bottom,
          rgba(255, 255, 255, 0.08) 0px,
          rgba(255, 255, 255, 0.08) 1px,
          transparent 1px,
          transparent 40px
        );
    }
  }
</style>

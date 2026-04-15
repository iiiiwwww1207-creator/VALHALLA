'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { ContactShadows } from '@react-three/drei';
import {
  VRMExpressionPresetName,
  VRMLoaderPlugin,
  VRMUtils,
  type VRM,
} from '@pixiv/three-vrm';
import { Group, Vector3 } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { AvatarPlaceholder } from '@/components/avatar-placeholder';

type AvatarMood = 'happy' | 'neutral' | 'sad';

interface VRMAvatarProps {
  characterId: string;
  name: string;
  mood?: AvatarMood;
  isSpeaking?: boolean;
  modelUrl?: string;
  className?: string;
}

interface LoadedVRMModelProps {
  modelUrl: string;
  mood: AvatarMood;
  isSpeaking: boolean;
  onReady: () => void;
  onError: () => void;
}

function LoadedVRMModel({
  modelUrl,
  mood,
  isSpeaking,
  onReady,
  onError,
}: LoadedVRMModelProps) {
  const { camera } = useThree();
  const targetPosition = useMemo(() => new Vector3(), []);
  const vrmRef = useRef<VRM | null>(null);
  const rootGroupRef = useRef<Group>(null);
  const blinkRef = useRef({
    startedAt: -1,
    duration: 0.16,
    nextBlinkAt: 1.4,
  });

  useEffect(() => {
    let cancelled = false;
    const loader = new GLTFLoader();

    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      modelUrl,
      (gltf) => {
        if (cancelled) {
          return;
        }

        const vrm = gltf.userData.vrm as VRM | undefined;

        if (!vrm) {
          onError();
          return;
        }

        VRMUtils.rotateVRM0(vrm);
        VRMUtils.combineSkeletons(vrm.scene);

        vrm.scene.position.set(0, -1.1, 0);
        if (vrm.lookAt) {
          vrm.lookAt.target = camera;
        }
        vrmRef.current = vrm;
        onReady();
      },
      undefined,
      () => {
        if (!cancelled) {
          onError();
        }
      }
    );

    return () => {
      cancelled = true;

      if (vrmRef.current) {
        VRMUtils.deepDispose(vrmRef.current.scene);
        vrmRef.current = null;
      }
    };
  }, [camera, modelUrl, onError, onReady]);

  useFrame((state, delta) => {
    const vrm = vrmRef.current;
    const rootGroup = rootGroupRef.current;

    if (!vrm || !rootGroup) {
      return;
    }

    const elapsed = state.clock.getElapsedTime();
    const chestBone =
      vrm.humanoid.getNormalizedBoneNode('chest') ??
      vrm.humanoid.getNormalizedBoneNode('spine');

    rootGroup.position.y = Math.sin(elapsed * 1.2) * 0.04;
    rootGroup.rotation.z = Math.sin(elapsed * 0.9) * 0.04;
    rootGroup.rotation.y = Math.sin(elapsed * 0.45) * 0.08;

    if (chestBone) {
      chestBone.rotation.x = Math.sin(elapsed * 2.4) * 0.025;
    }

    const expressionManager = vrm.expressionManager;
    if (expressionManager) {
      if (elapsed >= blinkRef.current.nextBlinkAt) {
        blinkRef.current.startedAt = elapsed;
        blinkRef.current.duration = 0.12 + Math.random() * 0.06;
        blinkRef.current.nextBlinkAt = elapsed + 2.4 + Math.random() * 2.8;
      }

      let blinkWeight = 0;
      if (blinkRef.current.startedAt >= 0) {
        const blinkProgress =
          (elapsed - blinkRef.current.startedAt) / blinkRef.current.duration;

        if (blinkProgress >= 0 && blinkProgress <= 1) {
          blinkWeight =
            blinkProgress < 0.5
              ? blinkProgress * 2
              : (1 - blinkProgress) * 2;
        }
      }

      const mouthWeight = isSpeaking
        ? 0.12 + (Math.sin(elapsed * 18) * 0.5 + 0.5) * 0.62
        : 0;

      expressionManager.setValue(VRMExpressionPresetName.Blink, blinkWeight);
      expressionManager.setValue(
        VRMExpressionPresetName.Happy,
        mood === 'happy' ? 0.58 : 0
      );
      expressionManager.setValue(
        VRMExpressionPresetName.Neutral,
        mood === 'neutral' ? 0.2 : 0
      );
      expressionManager.setValue(
        VRMExpressionPresetName.Relaxed,
        mood === 'neutral' ? 0.1 : 0
      );
      expressionManager.setValue(
        VRMExpressionPresetName.Sad,
        mood === 'sad' ? 0.52 : 0
      );
      expressionManager.setValue(VRMExpressionPresetName.Aa, mouthWeight);
      expressionManager.setValue(VRMExpressionPresetName.Oh, mouthWeight * 0.35);
      expressionManager.setValue(VRMExpressionPresetName.Ee, mouthWeight * 0.18);
      expressionManager.update();
    }

    if (vrm.lookAt) {
      camera.getWorldPosition(targetPosition);
      targetPosition.y += 0.1;
      vrm.lookAt.lookAt(targetPosition);
    }

    vrm.update(delta);
  });

  return (
    <group ref={rootGroupRef} position={[0, 0, 0]}>
      {vrmRef.current && <primitive object={vrmRef.current.scene} />}
    </group>
  );
}

export function VRMAvatar({
  characterId,
  name,
  mood = 'neutral',
  isSpeaking = false,
  modelUrl = '/models/default.vrm',
  className = '',
}: VRMAvatarProps) {
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const handleReady = useCallback(() => {
    setStatus('ready');
  }, []);
  const handleError = useCallback(() => {
    setStatus('error');
  }, []);

  return (
    <div
      className={`relative overflow-hidden rounded-[32px] border border-white/70 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.22),_transparent_26%),linear-gradient(180deg,_rgba(255,255,255,0.95)_0%,_rgba(251,232,255,0.88)_100%)] shadow-[0_24px_60px_rgba(232,93,117,0.18)] ${className}`}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-center justify-between px-4 py-3">
        <span className="rounded-full bg-white/80 px-3 py-1 text-[11px] font-semibold tracking-[0.2em] text-primary backdrop-blur">
          VRM LIVE
        </span>
        <span
          className={`rounded-full px-3 py-1 text-[11px] font-semibold backdrop-blur ${
            isSpeaking
              ? 'bg-primary text-primary-foreground'
              : 'bg-white/80 text-muted-foreground'
          }`}
        >
          {isSpeaking ? 'VOICE ON AIR' : 'STANDBY'}
        </span>
      </div>

      {status !== 'ready' && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-[linear-gradient(180deg,_rgba(255,248,243,0.92)_0%,_rgba(250,242,255,0.94)_100%)]">
          <AvatarPlaceholder
            characterId={characterId}
            name={name}
            size="lg"
            className="h-28 w-28 text-3xl shadow-[0_18px_35px_rgba(232,93,117,0.16)]"
          />
          <div className="text-center">
            <p className="font-display text-lg font-bold text-foreground">
              {status === 'loading' ? 'アバターを準備中...' : 'VRMを読み込めませんでした'}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {status === 'loading'
                ? '読み込み完了まではプレースホルダーを表示します'
                : 'プレースホルダー表示で育成はそのまま使えます'}
            </p>
          </div>
        </div>
      )}

      <div
        className={`h-[200px] w-full transition-opacity duration-500 sm:h-[240px] ${
          status === 'ready' ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <Canvas camera={{ position: [0, 1.28, 2.15], fov: 24 }} gl={{ alpha: true }}>
          <ambientLight intensity={1.25} />
          <directionalLight position={[1.5, 2.2, 2.4]} intensity={1.9} color="#fff3ef" />
          <directionalLight position={[-2, 1.5, -1.4]} intensity={0.8} color="#d8c8ff" />
          <LoadedVRMModel
            modelUrl={modelUrl}
            mood={mood}
            isSpeaking={isSpeaking}
            onReady={handleReady}
            onError={handleError}
          />
          <ContactShadows
            position={[0, -1.35, 0]}
            opacity={0.3}
            scale={4.2}
            blur={2.2}
            far={2.8}
            color="#b26b7a"
          />
        </Canvas>
      </div>
    </div>
  );
}

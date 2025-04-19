/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import {onRequest} from "firebase-functions/v2/https";
import * as logger from "firebase-functions/logger";
import * as admin from "firebase-admin";

// Start writing functions
// https://firebase.google.com/docs/functions/typescript

// Firestore初期化（すでに初期化済みならスキップ）
if (!admin.apps.length) {
  admin.initializeApp();
  // エミュレーター用設定
  if (process.env.FIRESTORE_EMULATOR_HOST) {
    admin.firestore().settings({
      host: process.env.FIRESTORE_EMULATOR_HOST,
      ssl: false,
    });
  }
}
const db = admin.firestore();

export const helloWorld = onRequest((request, response) => {
  logger.info("Hello logs!", {structuredData: true});
  response.send("Hello from Firebase!");
});

export const addSampleData = onRequest(async (req, res) => {
  try {
    const data = req.body || { message: "sample", timestamp: Date.now() };
    const docRef = await db.collection("samples").add(data);
    res.status(200).json({ id: docRef.id, ...data });
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

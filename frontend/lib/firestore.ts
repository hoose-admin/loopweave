import {
  doc,
  getDoc,
  setDoc,
  updateDoc,
  collection,
  query,
  where,
  getDocs,
} from 'firebase/firestore';
import { db } from './firebase';
import { User } from '@/types';

const USERS_COLLECTION = 'users';

export const getUserProfile = async (uid: string): Promise<User | null> => {
  try {
    const userDoc = await getDoc(doc(db, USERS_COLLECTION, uid));
    if (userDoc.exists()) {
      return { uid, ...userDoc.data() } as User;
    }
    return null;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    return null;
  }
};

export const createUserProfile = async (user: User): Promise<boolean> => {
  try {
    await setDoc(doc(db, USERS_COLLECTION, user.uid), {
      ...user,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    return true;
  } catch (error) {
    console.error('Error creating user profile:', error);
    return false;
  }
};

export const updateUserProfile = async (uid: string, updates: Partial<User>): Promise<boolean> => {
  try {
    await updateDoc(doc(db, USERS_COLLECTION, uid), {
      ...updates,
      updatedAt: new Date().toISOString(),
    });
    return true;
  } catch (error) {
    console.error('Error updating user profile:', error);
    return false;
  }
};

export const getUserFavorites = async (uid: string): Promise<string[]> => {
  try {
    const userProfile = await getUserProfile(uid);
    return userProfile?.favorites || [];
  } catch (error) {
    console.error('Error fetching favorites:', error);
    return [];
  }
};

export const addFavorite = async (uid: string, symbol: string): Promise<boolean> => {
  try {
    const userProfile = await getUserProfile(uid);
    const favorites = userProfile?.favorites || [];
    
    if (!favorites.includes(symbol)) {
      await updateUserProfile(uid, { favorites: [...favorites, symbol] });
    }
    return true;
  } catch (error) {
    console.error('Error adding favorite:', error);
    return false;
  }
};

export const removeFavorite = async (uid: string, symbol: string): Promise<boolean> => {
  try {
    const userProfile = await getUserProfile(uid);
    const favorites = userProfile?.favorites || [];
    
    await updateUserProfile(uid, {
      favorites: favorites.filter((s) => s !== symbol),
    });
    return true;
  } catch (error) {
    console.error('Error removing favorite:', error);
    return false;
  }
};


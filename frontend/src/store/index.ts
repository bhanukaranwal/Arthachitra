import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import chartSlice from './chartSlice';
import orderBookSlice from './orderBookSlice';
import themeSlice from './themeSlice';
import authSlice from './authSlice';
import portfolioSlice from './portfolioSlice';

export const store = configureStore({
  reducer: {
    chart: chartSlice,
    orderBook: orderBookSlice,
    theme: themeSlice,
    auth: authSlice,
    portfolio: portfolioSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export const createFormSubmitHandler = <T>(
  onSubmit: (data: T | FormData) => Promise<void> | void,
  type: "application/json" | "multipart/form-data" = "application/json",
) => {
  return async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data =
      type === "application/json"
        ? (Object.fromEntries(new FormData(e.currentTarget)) as unknown as T)
        : new FormData(e.currentTarget);

    await onSubmit(data);
  };
};
